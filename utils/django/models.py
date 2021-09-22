from django.core.exceptions import ImproperlyConfigured

try:
    from encrypted_fields import fields
except ImportError:
    raise ImproperlyConfigured("Couldn't find the the 3rd party app "
                               "django-searchable-encrypted-fields which is required for "
                               "the database backend.")

from utils.django.forms import PasswordField


class PasswordModelField(fields.EncryptedCharField):

    def formfield(self, **kwargs):
        defaults = {'form_class': PasswordField}
        defaults.update(kwargs)
        return super(PasswordModelField, self).formfield(**defaults)


def defaults_dict(model, row, *args):
    fields = [f.name for f in model._meta.local_fields if f.name not in args]
    defaults = dict(
        (key, value) for key, value in row.items() if key in fields
    )
    return defaults
