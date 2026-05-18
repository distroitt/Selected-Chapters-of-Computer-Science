from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Sum
from django.urls import reverse

from .validators import validate_adult


phone_validator = RegexValidator(
    regex=r"^\+375 \((25|29|33|44)\) \d{3}-\d{2}-\d{2}$",
    message="Телефон должен быть в формате +375 (29) XXX-XX-XX.",
)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("изменено", auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField("название", max_length=120, unique=True)
    description = models.TextField("описание", blank=True)

    class Meta:
        verbose_name = "категория товара"
        verbose_name_plural = "категории товаров"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    sku = models.CharField("артикул", max_length=40, unique=True)
    name = models.CharField("название", max_length=160)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    price = models.DecimalField("розничная цена", max_digits=10, decimal_places=2)
    description = models.TextField("описание", blank=True)
    image_url = models.URLField("ссылка на изображение", blank=True)
    suppliers = models.ManyToManyField("Supplier", through="SupplierProduct", related_name="products")

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"pk": self.pk})

    @property
    def purchased_quantity(self):
        return (
            SupplyPurchase.objects.filter(supplier_product__product=self).aggregate(total=Sum("quantity"))[
                "total"
            ]
            or 0
        )

    @property
    def sold_quantity(self):
        return self.sale_items.aggregate(total=Sum("quantity"))["total"] or 0

    @property
    def stock_quantity(self):
        return self.purchased_quantity - self.sold_quantity


class Supplier(TimeStampedModel):
    name = models.CharField("название", max_length=160, unique=True)
    address = models.CharField("адрес", max_length=255)
    phone = models.CharField("телефон", max_length=19, validators=[phone_validator])
    email = models.EmailField("email", blank=True)

    class Meta:
        verbose_name = "поставщик"
        verbose_name_plural = "поставщики"
        ordering = ["name"]

    def __str__(self):
        return self.name


class SupplierProduct(TimeStampedModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    current_purchase_price = models.DecimalField(
        "текущая закупочная цена", max_digits=10, decimal_places=2
    )
    is_active = models.BooleanField("активно", default=True)

    class Meta:
        verbose_name = "товар поставщика"
        verbose_name_plural = "товары поставщиков"
        constraints = [
            models.UniqueConstraint(fields=["supplier", "product"], name="unique_supplier_product")
        ]

    def __str__(self):
        return f"{self.supplier} -> {self.product}"


class PriceChange(TimeStampedModel):
    supplier_product = models.ForeignKey(
        SupplierProduct, on_delete=models.CASCADE, related_name="price_changes"
    )
    effective_date = models.DateField("дата изменения")
    new_price = models.DecimalField("новая цена", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "изменение цены поставщика"
        verbose_name_plural = "изменения цен поставщиков"
        ordering = ["-effective_date"]

    def __str__(self):
        return f"{self.supplier_product}: {self.new_price} c {self.effective_date}"


class Customer(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")
    full_name = models.CharField("ФИО", max_length=180)
    birth_date = models.DateField("дата рождения", validators=[validate_adult])
    phone = models.CharField("телефон", max_length=19, validators=[phone_validator])
    address = models.CharField("адрес", max_length=255, blank=True)

    class Meta:
        verbose_name = "постоянный клиент"
        verbose_name_plural = "постоянные клиенты"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class Employee(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_profile")
    full_name = models.CharField("ФИО", max_length=180)
    birth_date = models.DateField("дата рождения", validators=[validate_adult])
    position = models.CharField("должность", max_length=120)
    phone = models.CharField("телефон", max_length=19, validators=[phone_validator])
    email = models.EmailField("email")
    photo_url = models.URLField("фото", blank=True)

    class Meta:
        verbose_name = "сотрудник"
        verbose_name_plural = "сотрудники"
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name}, {self.position}"


class SupplyPurchase(TimeStampedModel):
    supplier_product = models.ForeignKey(
        SupplierProduct, on_delete=models.PROTECT, related_name="purchases"
    )
    purchase_date = models.DateField("дата закупки")
    quantity = models.PositiveIntegerField("количество", validators=[MinValueValidator(1)])
    unit_price = models.DecimalField("цена за единицу", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "закупка у поставщика"
        verbose_name_plural = "закупки у поставщиков"
        ordering = ["-purchase_date"]

    @property
    def total_cost(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.supplier_product.product} x {self.quantity}"


class PromoCode(TimeStampedModel):
    code = models.CharField("код", max_length=40, unique=True)
    description = models.CharField("описание", max_length=255)
    discount_percent = models.PositiveIntegerField(
        "скидка, %", validators=[MinValueValidator(1), MaxValueValidator(90)]
    )
    active = models.BooleanField("действует", default=True)
    valid_until = models.DateField("действует до")

    class Meta:
        verbose_name = "промокод"
        verbose_name_plural = "промокоды и купоны"
        ordering = ["-active", "valid_until"]

    def __str__(self):
        return self.code


class Sale(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True)
    sale_date = models.DateTimeField("дата продажи", auto_now_add=True)

    class Meta:
        verbose_name = "продажа"
        verbose_name_plural = "продажи"
        ordering = ["-sale_date"]

    @property
    def total_amount(self):
        amount = sum(item.total_price for item in self.items.all())
        if self.promo_code and self.promo_code.active:
            return amount * (100 - self.promo_code.discount_percent) / 100
        return amount

    def __str__(self):
        return f"Продажа #{self.pk}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="sale_items")
    quantity = models.PositiveIntegerField("количество", validators=[MinValueValidator(1)])
    unit_price = models.DecimalField("цена за единицу", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "позиция продажи"
        verbose_name_plural = "позиции продаж"

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product} x {self.quantity}"


class Article(TimeStampedModel):
    title = models.CharField("заголовок", max_length=180)
    summary = models.CharField("краткое содержание", max_length=255)
    content = models.TextField("текст статьи")
    image_url = models.URLField("изображение", blank=True)
    published_at = models.DateTimeField("дата публикации")

    class Meta:
        verbose_name = "новость"
        verbose_name_plural = "новости"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title


class CompanyInfo(TimeStampedModel):
    name = models.CharField("название компании", max_length=160)
    about = models.TextField("о компании")
    requisites = models.TextField("реквизиты", blank=True)
    logo_url = models.URLField("логотип", blank=True)

    class Meta:
        verbose_name = "информация о компании"
        verbose_name_plural = "информация о компании"

    def __str__(self):
        return self.name


class FAQ(TimeStampedModel):
    question = models.CharField("вопрос", max_length=255)
    answer = models.TextField("ответ")

    class Meta:
        verbose_name = "термин и понятие"
        verbose_name_plural = "словарь терминов и понятий"
        ordering = ["-created_at"]

    def __str__(self):
        return self.question


class Vacancy(TimeStampedModel):
    title = models.CharField("вакансия", max_length=160)
    description = models.TextField("описание")
    salary = models.CharField("зарплата", max_length=120, blank=True)
    active = models.BooleanField("активна", default=True)

    class Meta:
        verbose_name = "вакансия"
        verbose_name_plural = "вакансии"
        ordering = ["-active", "title"]

    def __str__(self):
        return self.title


class Review(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField("имя", max_length=120)
    rating = models.PositiveIntegerField("оценка", validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField("текст")

    class Meta:
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}: {self.rating}/5"


class PickupPoint(TimeStampedModel):
    name = models.CharField("точка самовывоза", max_length=160)
    address = models.CharField("адрес", max_length=255)
    schedule = models.CharField("график", max_length=160)

    class Meta:
        verbose_name = "точка самовывоза"
        verbose_name_plural = "точки самовывоза"
        ordering = ["name"]

    def __str__(self):
        return self.name
