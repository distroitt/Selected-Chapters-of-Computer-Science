from django.contrib import admin

from .models import (
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


class SupplierProductInline(admin.TabularInline):
    model = SupplierProduct
    extra = 1
    autocomplete_fields = ["product"]


class PriceChangeInline(admin.TabularInline):
    model = PriceChange
    extra = 0


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    autocomplete_fields = ["product"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "name",
        "category",
        "price",
        "purchased_quantity",
        "sold_quantity",
        "stock_quantity",
        "created_at",
        "updated_at",
    )
    list_filter = ("category", "created_at")
    search_fields = ("sku", "name", "description")
    inlines = [SupplierProductInline]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "address")
    search_fields = ("name", "phone", "address")
    inlines = [SupplierProductInline]


@admin.register(SupplierProduct)
class SupplierProductAdmin(admin.ModelAdmin):
    list_display = ("supplier", "product", "current_purchase_price", "is_active")
    list_filter = ("is_active", "supplier")
    search_fields = ("supplier__name", "product__name", "product__sku")
    inlines = [PriceChangeInline]


@admin.register(SupplyPurchase)
class SupplyPurchaseAdmin(admin.ModelAdmin):
    list_display = ("supplier_product", "purchase_date", "quantity", "unit_price", "total_cost")
    list_filter = ("purchase_date", "supplier_product__supplier")
    search_fields = ("supplier_product__supplier__name", "supplier_product__product__name")


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "employee", "promo_code", "sale_date", "total_amount")
    list_filter = ("sale_date", "promo_code")
    autocomplete_fields = ["customer", "employee", "promo_code"]
    inlines = [SaleItemInline]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "user", "created_at")
    search_fields = ("full_name", "phone", "user__username")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position", "phone", "email")
    list_filter = ("position",)
    search_fields = ("full_name", "phone", "email")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "published_at", "created_at")
    list_filter = ("published_at",)
    search_fields = ("title", "summary", "content")


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percent", "active", "valid_until")
    list_filter = ("active", "valid_until")
    search_fields = ("code", "description")


admin.site.register(Category)
admin.site.register(CompanyInfo)
admin.site.register(FAQ)
admin.site.register(PickupPoint)
admin.site.register(Review)
admin.site.register(SaleItem)
admin.site.register(Vacancy)
