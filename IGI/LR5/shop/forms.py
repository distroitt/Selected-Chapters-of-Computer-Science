from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Customer, Product, PromoCode, Review, SaleItem, Supplier, SupplyPurchase
from .models import phone_validator
from .validators import validate_adult


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    full_name = forms.CharField(label="ФИО", max_length=180)
    birth_date = forms.DateField(
        label="Дата рождения",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    phone = forms.CharField(
        label="Телефон",
        help_text="+375 (29) XXX-XX-XX",
        widget=forms.TextInput(
            attrs={"pattern": r"^\+375 \((25|29|33|44)\) \d{3}-\d{2}-\d{2}$"}
        ),
    )
    address = forms.CharField(label="Адрес", max_length=255, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "full_name", "birth_date", "phone", "address")

    def clean_birth_date(self):
        birth_date = self.cleaned_data["birth_date"]
        validate_adult(birth_date)
        return birth_date

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        phone_validator(phone)
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            Customer.objects.create(
                user=user,
                full_name=self.cleaned_data["full_name"],
                birth_date=self.cleaned_data["birth_date"],
                phone=self.cleaned_data["phone"],
                address=self.cleaned_data["address"],
            )
        return user


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("sku", "name", "category", "price", "description", "image_url")
        widgets = {
            "price": forms.NumberInput(attrs={"min": "0.01", "step": "0.01"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ("name", "address", "phone", "email")
        widgets = {
            "phone": forms.TextInput(
                attrs={"pattern": r"^\+375 \((25|29|33|44)\) \d{3}-\d{2}-\d{2}$"}
            )
        }


class SupplyPurchaseForm(forms.ModelForm):
    class Meta:
        model = SupplyPurchase
        fields = ("supplier_product", "purchase_date", "quantity", "unit_price")
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
            "quantity": forms.NumberInput(attrs={"min": 1}),
            "unit_price": forms.NumberInput(attrs={"min": "0.01", "step": "0.01"}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "text")
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "text": forms.Textarea(attrs={"rows": 4, "minlength": 10}),
        }


class BuyProductForm(forms.ModelForm):
    promo_code = forms.CharField(
        label="Промокод",
        max_length=40,
        required=False,
        help_text="Введите код, если он у вас есть.",
    )

    class Meta:
        model = SaleItem
        fields = ("quantity", "promo_code")
        widgets = {"quantity": forms.NumberInput(attrs={"min": 1})}

    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product
        if product is not None:
            self.fields["quantity"].widget.attrs["max"] = max(product.stock_quantity, 0)
            self.fields["quantity"].help_text = f"Доступно на складе: {product.stock_quantity}."

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if self.product is None:
            return quantity

        stock_quantity = self.product.stock_quantity
        if stock_quantity <= 0:
            raise forms.ValidationError("Товар закончился на складе.")
        if quantity > stock_quantity:
            raise forms.ValidationError(f"На складе доступно только {stock_quantity} шт.")
        return quantity

    def clean_promo_code(self):
        code = self.cleaned_data["promo_code"].strip()
        if not code:
            return None

        promo = PromoCode.objects.filter(code__iexact=code).first()
        if promo is None:
            raise forms.ValidationError("Такого промокода нет.")
        if not promo.active:
            raise forms.ValidationError("Этот промокод уже в архиве.")
        if promo.valid_until < timezone.localdate():
            raise forms.ValidationError("Срок действия промокода истек.")
        return promo
