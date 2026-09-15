from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from shop.models import (
    Article,
    Category,
    Customer,
    Partner,
    PickupPoint,
    Product,
    PromoCode,
    Sale,
    SaleItem,
    Supplier,
    SupplierProduct,
    SupplyPurchase,
)


class ViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Игрушки")
        self.product = Product.objects.create(
            sku="T-1",
            name="Мяч",
            category=self.category,
            price=Decimal("8.50"),
            description="Игрушка",
        )
        self.supplier = Supplier.objects.create(
            name="Zoo Trade", address="Минск", phone="+375 (29) 111-22-33"
        )
        self.supplier_product = SupplierProduct.objects.create(
            supplier=self.supplier,
            product=self.product,
            current_purchase_price=Decimal("5.00"),
        )
        SupplyPurchase.objects.create(
            supplier_product=self.supplier_product,
            purchase_date=date.today(),
            quantity=5,
            unit_price=Decimal("5.00"),
        )
        Article.objects.create(
            title="Новость",
            summary="Коротко",
            content="Полный текст",
            published_at=timezone.now(),
        )
        self.user = User.objects.create_user(username="buyer", password="pass12345")
        Customer.objects.create(
            user=self.user,
            full_name="Иван Иванов",
            birth_date=date(1990, 1, 1),
            phone="+375 (29) 123-45-67",
        )
        self.staff = User.objects.create_user(
            username="staff", password="pass12345", is_staff=True
        )
        self.pickup = PickupPoint.objects.create(
            name="Центр", address="Минск", schedule="10:00-20:00"
        )

    def test_home_page_loads_latest_article(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Новость")

    def test_home_page_loads_partner_from_database(self):
        Partner.objects.create(
            name="Purina",
            website_url="https://www.purina.com/",
            logo_path="images/partners/purina.svg",
        )

        response = self.client.get(reverse("home"))

        self.assertContains(response, "Purina")
        self.assertContains(response, "images/partners/purina.svg")

    def test_catalog_search_finds_product(self):
        response = self.client.get(reverse("products"), {"q": "Мяч"})

        self.assertContains(response, "Мяч")

    def test_product_create_requires_staff(self):
        response = self.client.get(reverse("product_create"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_staff_can_create_supplier(self):
        self.client.login(username="staff", password="pass12345")
        response = self.client.post(
            reverse("supplier_create"),
            {
                "name": "Pet Supply",
                "address": "Минск",
                "phone": "+375 (33) 111-22-33",
                "email": "zoo@example.com",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Supplier.objects.filter(name="Pet Supply").exists())

    def test_logged_user_can_buy_product(self):
        self.client.login(username="buyer", password="pass12345")
        response = self.client.post(reverse("buy_product", args=[self.product.pk]), {"quantity": 2})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.customer_profile.sale_set.count(), 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 3)

    def test_cart_supports_add_increase_decrease_and_remove(self):
        self.client.post(reverse("add_to_cart", args=[self.product.pk]), {"quantity": 2})
        response = self.client.get(reverse("cart"))
        self.assertContains(response, "17,00 BYN")

        self.client.post(
            reverse("update_cart", args=[self.product.pk]), {"action": "increase"}
        )
        self.assertEqual(self.client.session["cart"][str(self.product.pk)], 3)

        self.client.post(
            reverse("update_cart", args=[self.product.pk]), {"action": "decrease"}
        )
        self.assertEqual(self.client.session["cart"][str(self.product.pk)], 2)

        self.client.post(reverse("remove_from_cart", args=[self.product.pk]))
        self.assertNotIn(str(self.product.pk), self.client.session["cart"])

    def test_checkout_creates_sale_and_clears_cart(self):
        self.client.post(reverse("add_to_cart", args=[self.product.pk]), {"quantity": 2})
        self.client.login(username="buyer", password="pass12345")

        response = self.client.post(
            reverse("checkout"),
            {
                "delivery_method": "pickup",
                "pickup_point": self.pickup.pk,
                "address": "",
                "cardholder": "IVAN IVANOV",
                "card_number": "1111 2222 3333 4444",
                "expiry": "12/30",
                "cvv": "123",
                "promo_code": "",
                "accept_terms": "on",
            },
        )

        self.assertRedirects(response, reverse("account"))
        sale = self.user.customer_profile.sale_set.get()
        self.assertEqual(sale.items.get().quantity, 2)
        self.assertEqual(self.client.session["cart"], {})

    def test_html_demo_contains_required_semantic_elements(self):
        response = self.client.get(reverse("html_demo"))

        self.assertContains(response, "<article>", html=False)
        self.assertContains(response, "<video", html=False)
        self.assertContains(response, "<audio", html=False)
        self.assertContains(response, 'headers="food range min"', html=False)

    def test_user_cannot_buy_more_than_stock_quantity(self):
        self.client.login(username="buyer", password="pass12345")
        response = self.client.post(reverse("buy_product", args=[self.product.pk]), {"quantity": 6})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "На складе доступно только 5 шт.")
        self.assertEqual(self.user.customer_profile.sale_set.count(), 0)

    def test_logged_user_can_apply_promo_code(self):
        promo = PromoCode.objects.create(
            code="PET10",
            description="Скидка",
            discount_percent=10,
            active=True,
            valid_until=date.today() + timedelta(days=7),
        )
        self.client.login(username="buyer", password="pass12345")

        response = self.client.post(
            reverse("buy_product", args=[self.product.pk]),
            {"quantity": 2, "promo_code": "pet10"},
        )

        sale = self.user.customer_profile.sale_set.get()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(sale.promo_code, promo)
        self.assertEqual(sale.total_amount, Decimal("15.30"))

    def test_expired_promo_code_is_rejected(self):
        PromoCode.objects.create(
            code="OLD",
            description="Старая скидка",
            discount_percent=10,
            active=True,
            valid_until=date.today() - timedelta(days=1),
        )
        self.client.login(username="buyer", password="pass12345")

        response = self.client.post(
            reverse("buy_product", args=[self.product.pk]),
            {"quantity": 2, "promo_code": "OLD"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Срок действия промокода истек")
        self.assertEqual(self.user.customer_profile.sale_set.count(), 0)

    def test_api_requires_authentication(self):
        response = self.client.get(reverse("products_api"))

        self.assertEqual(response.status_code, 302)

    def test_api_returns_products_for_authenticated_user(self):
        self.client.login(username="buyer", password="pass12345")
        response = self.client.get(reverse("products_api"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["products"][0]["sku"], "T-1")

    def test_statistics_page_contains_matplotlib_chart(self):
        sale = Sale.objects.create(customer=self.user.customer_profile)
        SaleItem.objects.create(
            sale=sale,
            product=self.product,
            quantity=2,
            unit_price=self.product.price,
        )
        self.client.login(username="buyer", password="pass12345")

        response = self.client.get(reverse("statistics"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data:image/png;base64,")

    def test_registration_creates_customer_profile(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newbuyer",
                "email": "new@example.com",
                "full_name": "Новый Покупатель",
                "birth_date": "1992-02-02",
                "phone": "+375 (44) 222-33-44",
                "address": "Минск",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Customer.objects.filter(user__username="newbuyer").exists())
