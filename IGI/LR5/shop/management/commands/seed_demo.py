from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from shop.models import (
    Article,
    Category,
    CompanyInfo,
    Customer,
    Employee,
    FAQ,
    PickupPoint,
    PriceChange,
    Product,
    PromoCode,
    Review,
    Sale,
    SaleItem,
    Supplier,
    SupplierProduct,
    SupplyPurchase,
    Vacancy,
)


class Command(BaseCommand):
    help = "Заполняет базу демо-данными."

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "is_staff": True,
                "is_superuser": True,
                "email": "admin@example.com",
            },
        )
        admin.is_staff = True
        admin.is_superuser = True
        admin.email = "admin@example.com"
        admin.set_password("admin12345")
        admin.save()

        customer_user, created = User.objects.get_or_create(
            username="buyer",
            defaults={
                "email": "buyer@example.com",
            },
        )
        customer_user.email = "buyer@example.com"
        if created:
            customer_user.set_password("buyer12345")
        customer_user.save()

        categories = [
            Category.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                },
            )[0]
            for name, description in [
                ("Корма", "Сухие и влажные корма для животных."),
                ("Игрушки", "Игрушки для активных питомцев."),
                ("Уход", "Гигиена и косметика для животных."),
                ("Амуниция", "Поводки, ошейники и переноски."),
            ]
        ]

        supplier_data = [
            ("PetSupply BY", "Минск, ул. Сурганова, 10", "+375 (29) 111-22-33"),
            ("ZooTrade", "Минск, пр. Независимости, 42", "+375 (33) 222-33-44"),
            ("Happy Paws", "Гродно, ул. Советская, 7", "+375 (44) 333-44-55"),
        ]

        suppliers = [
            Supplier.objects.get_or_create(
                name=name,
                defaults={
                    "address": address,
                    "phone": phone,
                    "email": f"{name.lower().replace(' ', '')}@example.com",
                },
            )[0]
            for name, address, phone in supplier_data
        ]

        product_data = [
            (
                "FD-001",
                "Корм для котят",
                categories[0],
                "18.90",
                "https://ir.ozone.ru/s3/multimedia-t/c1000/6674384801.jpg",
            ),
            (
                "FD-002",
                "Корм для собак крупных пород",
                categories[0],
                "45.50",
                "https://vetapteki.by/wp-content/uploads/prod/2025/07/G000109817_0_250715.jpg",
            ),
            (
                "FD-003",
                "Лакомство с курицей",
                categories[0],
                "7.20",
                "https://basket-09.wbbasket.ru/vol1276/part127609/127609151/images/big/1.webp",
            ),
            (
                "TY-001",
                "Мяч с пищалкой",
                categories[1],
                "9.50",
                "https://ir.ozone.ru/s3/multimedia-1-h/c1000/7212272741.jpg",
            ),
            (
                "TY-002",
                "Удочка-дразнилка",
                categories[1],
                "6.80",
                "https://ir.ozone.ru/s3/multimedia-v/c1000/6895764499.jpg",
            ),
            (
                "TY-003",
                "Канат для собак",
                categories[1],
                "12.40",
                "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSsCQ1lwX6O3qWkr8J1y2pkGdCnEmbPh1WvMw&s",
            ),
            (
                "CR-001",
                "Шампунь гипоаллергенный",
                categories[2],
                "15.00",
                "https://ir.ozone.ru/s3/multimedia-6/c1000/6643464882.jpg",
            ),
            (
                "CR-002",
                "Когтерез",
                categories[2],
                "11.30",
                "https://ir.ozone.ru/s3/multimedia-1/6416527741.jpg",
            ),
            (
                "EQ-001",
                "Ошейник светоотражающий",
                categories[3],
                "13.70",
                "https://basket-10.wbbasket.ru/vol1447/part144738/144738307/images/big/1.webp",
            ),
            (
                "EQ-002",
                "Переноска пластиковая",
                categories[3],
                "52.00",
                "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSey_Ngd_HZsnpyqhk4_J-yzcwwsQfc-JEZWg&s",
            ),
        ]

        products = []

        for sku, name, category, price, image_url in product_data:
            product, _ = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "category": category,
                    "price": Decimal(price),
                    "description": f"{name} для ежедневного ухода за питомцем.",
                    "image_url": image_url,
                },
            )
            products.append(product)

        supplier_products = []

        for index, product in enumerate(products):
            supplier = suppliers[index % len(suppliers)]

            relation, _ = SupplierProduct.objects.get_or_create(
                supplier=supplier,
                product=product,
                defaults={
                    "current_purchase_price": product.price * Decimal("0.72"),
                },
            )

            supplier_products.append(relation)

            PriceChange.objects.get_or_create(
                supplier_product=relation,
                effective_date=date.today() + timedelta(days=14),
                defaults={
                    "new_price": relation.current_purchase_price * Decimal("1.05"),
                },
            )

            SupplyPurchase.objects.get_or_create(
                supplier_product=relation,
                purchase_date=date.today() - timedelta(days=index + 1),
                defaults={
                    "quantity": 10 + index,
                    "unit_price": relation.current_purchase_price,
                },
            )

        Customer.objects.get_or_create(
            user=customer_user,
            defaults={
                "full_name": "Иванов Иван Иванович",
                "birth_date": date(1995, 5, 10),
                "phone": "+375 (29) 123-45-67",
                "address": "Минск, ул. Зоологическая, 1",
            },
        )

        employees_data = [
            {
                "username": "seller",
                "password": "seller12345",
                "email": "seller@example.com",
                "full_name": "Петрова Анна Сергеевна",
                "birth_date": date(1990, 8, 20),
                "position": "Менеджер по поставщикам",
                "phone": "+375 (33) 765-43-21",
                "photo_url": "https://static.vecteezy.com/system/resources/thumbnails/052/129/001/small/a-beautiful-young-business-woman-in-a-suit-photo.jpg",
            },
            {
                "username": "seller2",
                "password": "seller12345",
                "email": "seller2@example.com",
                "full_name": "Сидоров Максим Олегович",
                "birth_date": date(1988, 3, 14),
                "position": "Старший продавец",
                "phone": "+375 (29) 101-11-11",
                "photo_url": "https://img.freepik.com/free-photo/portrait-smiling-young-businessman-standing-with-arms-folded_171337-9909.jpg",
            },
            {
                "username": "seller3",
                "password": "seller12345",
                "email": "seller3@example.com",
                "full_name": "Козлова Мария Андреевна",
                "birth_date": date(1994, 11, 5),
                "position": "Продавец-консультант",
                "phone": "+375 (29) 102-22-22",
                "photo_url": "https://img.freepik.com/free-photo/portrait-young-woman-smiling_23-2149158572.jpg",
            },
            {
                "username": "seller4",
                "password": "seller12345",
                "email": "seller4@example.com",
                "full_name": "Морозов Дмитрий Павлович",
                "birth_date": date(1987, 6, 18),
                "position": "Специалист по складу",
                "phone": "+375 (29) 103-33-33",
                "photo_url": "https://img.freepik.com/free-photo/young-businessman-with-arms-crossed_23-2149158584.jpg",
            },
            {
                "username": "seller5",
                "password": "seller12345",
                "email": "seller5@example.com",
                "full_name": "Новикова Елена Викторовна",
                "birth_date": date(1992, 2, 27),
                "position": "Кассир",
                "phone": "+375 (29) 104-44-44",
                "photo_url": "https://img.freepik.com/free-photo/portrait-beautiful-young-woman-standing-grey-wall_231208-10760.jpg",
            },
            {
                "username": "seller6",
                "password": "seller12345",
                "email": "seller6@example.com",
                "full_name": "Орлов Артём Игоревич",
                "birth_date": date(1996, 9, 9),
                "position": "Продавец-консультант",
                "phone": "+375 (29) 105-55-55",
                "photo_url": "https://img.freepik.com/free-photo/handsome-young-man-smiling_23-2149158575.jpg",
            },
            {
                "username": "seller7",
                "password": "seller12345",
                "email": "seller7@example.com",
                "full_name": "Громова Ольга Николаевна",
                "birth_date": date(1989, 12, 1),
                "position": "Администратор магазина",
                "phone": "+375 (29) 106-66-66",
                "photo_url": "https://img.freepik.com/free-photo/portrait-young-businesswoman-smiling_23-2149158574.jpg",
            },
            {
                "username": "seller8",
                "password": "seller12345",
                "email": "seller8@example.com",
                "full_name": "Белов Кирилл Сергеевич",
                "birth_date": date(1991, 4, 22),
                "position": "Менеджер по продажам",
                "phone": "+375 (29) 107-77-77",
                "photo_url": "https://img.freepik.com/free-photo/smiling-young-businessman-standing-office_171337-10313.jpg",
            },
            {
                "username": "seller9",
                "password": "seller12345",
                "email": "seller9@example.com",
                "full_name": "Лебедева Наталья Романовна",
                "birth_date": date(1993, 7, 16),
                "position": "Специалист по клиентскому сервису",
                "phone": "+375 (29) 108-88-88",
                "photo_url": "https://img.freepik.com/free-photo/portrait-smiling-businesswoman_23-2149158573.jpg",
            },
            {
                "username": "seller10",
                "password": "seller12345",
                "email": "seller10@example.com",
                "full_name": "Фролов Алексей Денисович",
                "birth_date": date(1986, 10, 30),
                "position": "Товаровед",
                "phone": "+375 (29) 109-99-99",
                "photo_url": "https://img.freepik.com/free-photo/portrait-handsome-businessman_23-2149158581.jpg",
            },
        ]

        employees = []

        for data in employees_data:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "is_staff": True,
                    "email": data["email"],
                },
            )

            user.is_staff = True
            user.email = data["email"]

            if created:
                user.set_password(data["password"])

            user.save()

            employee_obj, _ = Employee.objects.get_or_create(
                user=user,
                defaults={
                    "full_name": data["full_name"],
                    "birth_date": data["birth_date"],
                    "position": data["position"],
                    "phone": data["phone"],
                    "email": data["email"],
                    "photo_url": data["photo_url"],
                },
            )

            employees.append(employee_obj)

        employee = employees[0]

        PromoCode.objects.get_or_create(
            code="PET10",
            defaults={
                "description": "Скидка для постоянных клиентов",
                "discount_percent": 10,
                "active": True,
                "valid_until": date.today() + timedelta(days=30),
            },
        )

        PromoCode.objects.get_or_create(
            code="OLDPET",
            defaults={
                "description": "Архивный купон",
                "discount_percent": 5,
                "active": False,
                "valid_until": date.today() - timedelta(days=10),
            },
        )

        customer = customer_user.customer_profile

        for index, product in enumerate(products[:5]):
            sale = Sale.objects.create(
                customer=customer,
                employee=employee,
            )

            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=index + 1,
                unit_price=product.price,
            )

        CompanyInfo.objects.get_or_create(
            name="PetCare Market",
            defaults={
                "about": "Зоомагазин продает корма, игрушки, средства ухода и аксессуары для домашних животных.",
                "requisites": "УНП 123456789\nIBAN BY00TEST00000000000000000000",
            },
        )

        Article.objects.get_or_create(
            title="Как выбрать корм для питомца",
            defaults={
                "summary": "Разбираем состав, возраст животного и особенности здоровья.",
                "content": "Подбирайте корм по возрасту, активности и рекомендациям ветеринара.",
                "published_at": timezone.now(),
            },
        )

        FAQ.objects.get_or_create(
            question="Артикул",
            defaults={
                "answer": "Уникальный код товара, по которому его ищут в каталоге и у поставщиков.",
            },
        )

        FAQ.objects.get_or_create(
            question="Поставка",
            defaults={
                "answer": "Факт закупки товара у поставщика с датой, количеством и ценой.",
            },
        )

        Vacancy.objects.get_or_create(
            title="Продавец-консультант",
            defaults={
                "description": "Консультация покупателей и работа с кассой.",
                "salary": "от 1200 BYN",
            },
        )

        Review.objects.get_or_create(
            user=customer_user,
            name="Иван",
            defaults={
                "rating": 5,
                "text": "Быстро нашли нужный корм и помогли с выбором игрушки.",
            },
        )

        PickupPoint.objects.get_or_create(
            name="Самовывоз Центр",
            defaults={
                "address": "Минск, ул. Ленина, 12",
                "schedule": "Пн-Пт 10:00-20:00",
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Демо-данные созданы. "
                "admin/admin12345, buyer/buyer12345, "
                "seller/seller12345 ... seller10/seller12345"
            )
        )