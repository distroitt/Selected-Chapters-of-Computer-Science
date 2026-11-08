"""Отдельные браузерные проверки на временной тестовой БД Django.
Запуск: python manage.py test tests.browser_checks --noinput
Требует playwright и установленный Google Chrome/Chromium.
"""
from pathlib import Path
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.management import call_command
from playwright.sync_api import sync_playwright, expect


class BrowserChecks(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        call_command('seed_demo', verbosity=0)

    def setUp(self):
        super().setUp()
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True,
                                                    args=['--no-sandbox', '--disable-dev-shm-usage'])

    def tearDown(self):
        self.browser.close()
        self.playwright.stop()
        super().tearDown()

    def test_browser_workflows(self):
        context = self.browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(self.live_server_url)
        expect(page.locator('[data-counter]')).to_have_text('1/3')
        page.locator('[data-next]').click()
        expect(page.locator('[data-counter]')).to_have_text('2/3')
        page.locator('[data-prev]').click()
        page.locator('[data-prev]').click()
        expect(page.locator('[data-counter]')).to_have_text('3/3')
        page.locator('[data-pages] button').first.click()
        expect(page.locator('[data-counter]')).to_have_text('1/3')
        page.locator('#theme-toggle').click()
        page.reload()
        expect(page.locator('html')).to_have_attribute('data-theme', 'dark')

        page.goto(self.live_server_url + '/employees/')
        expect(page.locator('#employee-table tbody tr')).to_have_count(3)
        page.locator('#employee-table tbody input').first.check()
        page.locator('#employees-pages').get_by_role('button', name='2', exact=True).click()
        page.locator('#employee-table tbody input').first.check()
        page.locator('#bonus-button').click()
        expect(page.locator('#selection-count')).to_contain_text('Выбрано: 2')
        expect(page.locator('#bonus-result')).to_contain_text('премировать')
        page.locator('#employee-query').fill('фролов')
        page.locator('#employee-search button').click()
        expect(page.locator('#employee-table tbody tr')).to_have_count(1)
        page.locator('#employee-table tbody button').first.click()
        expect(page.locator('#employee-details')).to_contain_text('Фролов')
        page.locator('#employee-query').fill('неттакогосотрудника')
        page.locator('#employee-search button').click()
        expect(page.locator('#employee-table tbody')).to_contain_text('не найдены')
        page.locator('#employee-query').fill('')
        page.locator('#employee-search button').click()
        page.locator('[data-sort="full_name"]').click()
        expect(page.locator('th[aria-sort]')).to_have_attribute('aria-sort', 'descending')
        for phone in ['80291112233', '8 (029) 1112233', '+375 (29) 111-22-33', '+375 (29) 111 22 33']:
            self.assertTrue(page.evaluate('value => validateContactPhone(value)', phone))
        self.assertFalse(page.evaluate('validateContactPhone("123")'))
        self.assertTrue(page.evaluate('validateContactURL("https://example.com/a.html")'))
        self.assertFalse(page.evaluate('validateContactURL("site.ru/a.php")'))
        self.assertFalse(page.evaluate('validateContactURL("https://example.com")'))

        page.goto(self.live_server_url + '/accounts/login/?next=/employees/')
        page.locator('[name=username]').fill('admin')
        page.locator('[name=password]').fill('admin12345')
        page.locator('main button').click()
        page.wait_for_url('**/employees/')
        page.locator('#employee-add').click()
        form = page.locator('#employee-form')
        for name, value in {'full_name': 'Тестов Тест Тестович', 'position': 'Уход за питомцами',
                            'phone': '123', 'email': 'test@example.com',
                            'photo_url': 'https://example.com/photo.html'}.items():
            form.locator(f'[name={name}]').fill(value)
        expect(form.locator('[type=submit]')).to_be_disabled()
        expect(form.locator('[name=phone]')).to_have_attribute('aria-invalid', 'true')
        Path('/tmp/strweb-lr3-qa').mkdir(exist_ok=True)
        page.screenshot(path='/tmp/strweb-lr3-qa/employee-form-dark.png', full_page=True)
        form.locator('[name=phone]').fill('8 (029) 1112233')
        expect(form.locator('[type=submit]')).to_be_enabled()
        form.locator('[type=submit]').click()
        expect(page.locator('#employee-validation')).to_contain_text('сохранён в базе')
        page.reload()
        page.locator('#employee-query').fill('Тестов Тест')
        page.locator('#employee-search button').click()
        expect(page.locator('#employee-table tbody')).to_contain_text('Тестов Тест')
        page.goto(self.live_server_url)
        page.get_by_text('Настройки слайдера', exact=True).click()
        page.locator('#slider-form [name=delay]').fill('2')
        page.locator('#slider-form [name=loop]').uncheck()
        page.locator('#slider-form button').click()
        expect(page.locator('#slider-status')).to_contain_text('сохранены')
        page.reload()
        expect(page.locator('#slider-form [name=delay]')).to_have_value('2')
        expect(page.locator('[data-prev]')).to_be_disabled()

        page.goto(self.live_server_url + '/products/?q=Корм')
        expect(page.locator('.grid .item')).to_have_count(2)
        page.goto(self.live_server_url + '/products/')
        expect(page.locator('.grid .item')).to_have_count(3)
        page.locator('.pagination a').nth(1).click()
        expect(page.locator('.grid .item')).to_have_count(3)

        page.goto(self.live_server_url + '/js-lab/')
        expect(page.locator('#chart-status')).to_contain_text('Построено')
        self.assertEqual(page.evaluate('Chart.getChart("series-chart").data.datasets.length'), 2)
        page.locator('#generate-field').click()
        page.locator('#generate-field').click()
        expect(page.locator('.builder-field')).to_have_count(2)
        page.locator('.builder-field').first.locator('[data-attribute=placeholder]').fill('Проверка сохранения')
        page.locator('.builder-field').first.locator('[data-attribute=readonly]').check()
        page.reload()
        expect(page.locator('.builder-field')).to_have_count(2)
        expect(page.locator('.builder-field').first.locator('input').first).to_have_attribute('placeholder', 'Проверка сохранения')
        expect(page.locator('.builder-field').first.locator('input').first).to_have_attribute('readonly', '')
        page.locator('.builder-field').first.get_by_role('button').click()
        page.reload()
        expect(page.locator('.builder-field')).to_have_count(1)
        page.locator('#birth-date').fill('2000-01-01')
        page.locator('#birth-form button').click()
        expect(page.locator('#birth-result')).to_contain_text('суббота')
        dialogs = []
        page.on('dialog', lambda dialog: (dialogs.append(dialog.message), dialog.accept()))
        page.locator('#birth-date').fill('2020-01-01')
        page.locator('#birth-form button').click()
        self.assertTrue(any('родителей' in message for message in dialogs))
        expect(page.locator('#pupils-result')).to_contain_text('Иванова Анна')
        page.locator('#inheritance-style').select_option('prototype')
        for name, value in {'name': 'Игорь', 'surname': 'Петров', 'schoolClass': '9А'}.items():
            page.locator(f'#pupils-form [name={name}]').fill(value)
        page.locator('#pupils-form button').click()
        expect(page.locator('#pupils-result')).to_contain_text('Петров Игорь')
        with page.expect_download() as download:
            page.locator('#chart-save').click()
        self.assertEqual(download.value.suggested_filename, 'petcare-series-variant1.png')
        output = Path('/tmp/strweb-lr3-qa')
        output.mkdir(exist_ok=True)
        download.value.save_as(output / 'series.png')
        page.screenshot(path=str(output / 'lab-desktop.png'), full_page=True)
        for width, height in [(390, 844), (900, 400)]:
            page.set_viewport_size({'width': width, 'height': height})
            for route in ['/', '/employees/', '/products/', '/js-lab/']:
                page.goto(self.live_server_url + route)
                self.assertTrue(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), f'Overflow: {route} at {width}')
                page.screenshot(path=str(output / f'{route.strip("/") or "home"}-{width}.png'), full_page=True)
        # Ошибка загрузки не оставляет бесконечный прелоадер, доступен повтор.
        page.route('**/api/employees/', lambda route: route.abort())
        page.goto(self.live_server_url + '/employees/')
        expect(page.locator('#employees-retry')).to_be_visible()
        expect(page.locator('#employees-loader')).to_be_hidden()
        page.unroute('**/api/employees/')
        page.locator('#employees-retry').click()
        expect(page.locator('#employee-table tbody tr')).to_have_count(3)
        page.locator('#theme-toggle').click()
        page.screenshot(path=str(output / 'employees-light.png'), full_page=True)
        self.assertEqual(errors, [])
        context.close()

        # Обычный режим: таймер, hover-пауза, граница без loop и обратимый scroll.
        motion = self.browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='no-preference')
        page = motion.new_page()
        page.clock.install()
        page.goto(self.live_server_url)
        page.clock.fast_forward(2100)
        expect(page.locator('[data-counter]')).to_have_text('2/3')
        page.locator('[data-slider]').hover()
        page.clock.fast_forward(4000)
        expect(page.locator('[data-counter]')).to_have_text('2/3')
        page.mouse.move(0, 0)
        page.clock.fast_forward(2100)
        expect(page.locator('[data-counter]')).to_have_text('3/3')
        expect(page.locator('[data-next]')).to_be_disabled()
        page.clock.fast_forward(4000)
        expect(page.locator('[data-counter]')).to_have_text('3/3')
        position = page.locator('.pet-flight').evaluate('(scene) => scene.offsetTop - innerHeight / 2')
        def scroll_scene(y):
            page.evaluate('(y) => { scrollTo(0, y); dispatchEvent(new Event("scroll")); }', y)
            page.clock.run_for(100)
            return page.locator('.pet-flight img').first.evaluate('(image) => image.style.transform')
        transform = scroll_scene(position)
        self.assertNotEqual(transform, scroll_scene(position - 250))
        self.assertEqual(transform, scroll_scene(position))
        motion.close()
