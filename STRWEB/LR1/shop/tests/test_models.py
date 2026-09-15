from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from shop.models import Category, Customer, Product, Sale, SaleItem, Supplier, SupplierProduct, SupplyPurchase


class ModelValidationTests(TestCase):
    def test_phone_format_is_validated(self):
        supplier = Supplier(name="Bad Phone", address="Минск", phone="80291234567")

        with self.assertRaises(ValidationError):
            supplier.full_clean()

    def test_customer_must_be_adult(self):
        user = User.objects.create_user(username="teen")
        customer = Customer(
            user=user,
            full_name="Юный Клиент",
            birth_date=date.today(),
            phone="+375 (29) 123-45-67",
        )

        with self.assertRaises(ValidationError):
            customer.full_clean()

    def test_sale_total_uses_items(self):
        category = Category.objects.create(name="Корма")
        product = Product.objects.create(
            sku="A-1", name="Корм", category=category, price=Decimal("10.00")
        )
        sale = Sale.objects.create()
        SaleItem.objects.create(sale=sale, product=product, quantity=3, unit_price=Decimal("10.00"))

        self.assertEqual(sale.total_amount, Decimal("30.00"))

    def test_product_stock_is_purchase_quantity_minus_sold_quantity(self):
        category = Category.objects.create(name="Игрушки")
        supplier = Supplier.objects.create(
            name="Zoo Trade", address="Минск", phone="+375 (29) 111-22-33"
        )
        product = Product.objects.create(
            sku="T-1", name="Мяч", category=category, price=Decimal("8.50")
        )
        supplier_product = SupplierProduct.objects.create(
            supplier=supplier, product=product, current_purchase_price=Decimal("5.00")
        )
        SupplyPurchase.objects.create(
            supplier_product=supplier_product,
            purchase_date=date.today(),
            quantity=10,
            unit_price=Decimal("5.00"),
        )
        sale = Sale.objects.create()
        SaleItem.objects.create(sale=sale, product=product, quantity=3, unit_price=product.price)

        self.assertEqual(product.purchased_quantity, 10)
        self.assertEqual(product.sold_quantity, 3)
        self.assertEqual(product.stock_quantity, 7)
