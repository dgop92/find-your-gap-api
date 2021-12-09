from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import FileExtensionValidator as ExtensionValidator
from rest_framework.exceptions import ValidationError


class FileExtensionValidator(ExtensionValidator):
    def __call__(self, value):
        try:
            super().__call__(value)
        except DjangoValidationError as vd:
            raise ValidationError(vd.message % vd.params, code=vd.code)
