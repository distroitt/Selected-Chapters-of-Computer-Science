import pytest
from django.core.exceptions import ValidationError

from shop.models import phone_validator


@pytest.mark.parametrize(
    ("phone", "is_valid"),
    [
        ("+375 (29) 123-45-67", True),
        ("+375 (33) 000-11-22", True),
        ("80291234567", False),
        ("+375 (17) 123-45-67", False),
    ],
)
def test_phone_validator_parametrized(phone, is_valid):
    if is_valid:
        phone_validator(phone)
    else:
        with pytest.raises(ValidationError):
            phone_validator(phone)
