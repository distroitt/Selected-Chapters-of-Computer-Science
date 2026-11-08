from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Customer, PickupPoint, Product, PromoCode, Review, SaleItem, Supplier, SupplyPurchase
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


class CheckoutForm(forms.Form):
    delivery_method = forms.ChoiceField(
        label="Способ получения",
        choices=(("pickup", "Самовывоз"), ("courier", "Доставка курьером")),
        widget=forms.RadioSelect,
    )
    pickup_point = forms.ModelChoiceField(
        label="Точка самовывоза",
        queryset=PickupPoint.objects.none(),
        required=False,
    )
    address = forms.CharField(label="Адрес доставки", max_length=255, required=False)
    cardholder = forms.CharField(label="Имя владельца карты", max_length=120)
    card_number = forms.CharField(
        label="Номер карты",
        max_length=19,
        widget=forms.TextInput(
            attrs={"inputmode": "numeric", "autocomplete": "cc-number", "pattern": "[0-9 ]{16,19}"}
        ),
    )
    expiry = forms.CharField(
        label="Срок действия",
        max_length=5,
        widget=forms.TextInput(attrs={"placeholder": "MM/ГГ", "pattern": "(0[1-9]|1[0-2])/[0-9]{2}"}),
    )
    cvv = forms.CharField(
        label="CVV",
        min_length=3,
        max_length=3,
        widget=forms.PasswordInput(attrs={"inputmode": "numeric", "autocomplete": "cc-csc", "pattern": "[0-9]{3}"}),
    )
    promo_code = forms.CharField(label="Промокод", max_length=40, required=False)
    accept_terms = forms.BooleanField(label="Согласен с условиями оплаты")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pickup_point"].queryset = PickupPoint.objects.all()

    def clean_card_number(self):
        number = self.cleaned_data["card_number"].replace(" ", "")
        if not number.isdigit() or len(number) != 16:
            raise forms.ValidationError("Номер карты должен содержать 16 цифр.")
        return number

    def clean_cvv(self):
        cvv = self.cleaned_data["cvv"]
        if not cvv.isdigit():
            raise forms.ValidationError("CVV должен содержать 3 цифры.")
        return cvv

    def clean_promo_code(self):
        code = self.cleaned_data["promo_code"].strip()
        if not code:
            return None
        promo = PromoCode.objects.filter(code__iexact=code).first()
        if promo is None:
            raise forms.ValidationError("Такого промокода нет.")
        if not promo.active or promo.valid_until < timezone.localdate():
            raise forms.ValidationError("Промокод недействителен.")
        return promo

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get("delivery_method")
        if method == "pickup" and not cleaned_data.get("pickup_point"):
            self.add_error("pickup_point", "Выберите точку самовывоза.")
        if method == "courier" and not cleaned_data.get("address", "").strip():
            self.add_error("address", "Укажите адрес доставки.")
        return cleaned_data
