from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from shop.models import Employee, Product, Category


class LR3Tests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('lr3admin', password='test12345', is_staff=True)

    def test_new_pages(self):
        for name in ('employees_table', 'js_lab'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_contacts_from_database(self):
        Employee.objects.create(user=self.staff, full_name='Иванов Иван', birth_date='1990-01-01',
                                position='Консультант', phone='+375 (29) 111-22-33', email='a@example.com')
        response = self.client.get(reverse('employees_api'))
        self.assertEqual(response.json()['employees'][0]['full_name'], 'Иванов Иван')

    def test_employee_permissions_and_validation(self):
        url = reverse('employees_api')
        data = {'full_name': 'Иванов Иван Иванович', 'position': 'Уход за животными',
                'phone': '8 (029) 1112233', 'email': 'ivan@example.com',
                'photo_url': 'https://example.com/photo.html'}
        self.assertEqual(self.client.post(url, data).status_code, 403)
        self.client.force_login(self.staff)
        for phone in ('80291112233', '8 (029) 1112233', '+375 (29) 111-22-33', '+375 (29) 111 22 33'):
            data['phone'] = phone
            self.assertEqual(self.client.post(url, data).status_code, 201)
        for phone in ('123', 'abc80291112233', '+375 (29 1112233', '802911122334'):
            data['phone'] = phone
            self.assertEqual(self.client.post(url, data).status_code, 400)
        data['phone'] = '80291112233'
        for link in ('https://example.com', 'example.com/a.php', 'javascript:alert(1)'):
            data['photo_url'] = link
            self.assertEqual(self.client.post(url, data).status_code, 400)

    def test_slider_settings(self):
        url = reverse('slider_settings')
        self.assertEqual(self.client.post(url, {'delay': 2}).status_code, 403)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.post(url, {'delay': 0}).status_code, 400)
        self.assertEqual(self.client.post(url, {'delay': 2, 'loop': 'on', 'auto': 'on'}).status_code, 200)
        self.assertEqual(self.client.get(url).json()['delay'], 2)
        self.assertTrue(self.client.get(url).json()['loop'])

    def test_catalog_pagination_keeps_filters(self):
        category = Category.objects.create(name='Тест')
        for i in range(10):
            Product.objects.create(sku=f'LR3-{i}', name=f'Товар {i}', category=category, price=10)
        response = self.client.get(reverse('products'), {'q': 'Товар', 'sort': '-name'})
        self.assertEqual(len(response.context['products']), 3)
        self.assertContains(response, 'q=%D0%A2%D0%BE%D0%B2%D0%B0%D1%80')
        self.assertEqual(len(self.client.get(reverse('products'), {'page_size': 6}).context['products']), 6)

    def test_csrf_required_for_writes(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.staff)
        self.assertEqual(client.post(reverse('employees_api'), {}).status_code, 403)
