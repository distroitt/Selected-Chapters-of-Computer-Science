from datetime import date

from django.core.exceptions import ValidationError


def validate_adult(value):
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError("Клиенты и сотрудники должны быть старше 18 лет.")
