from rest_framework.exceptions import ValidationError


def validate_if_positive(value):
    if value is None:
        return value
    if value < 0:
        raise ValidationError("Value must be positive.")
    return value
