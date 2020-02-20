from django import forms
from django.utils.translation import ugettext as _
from bootstrap_modal_forms.forms import BSModalForm

from utils.django.validators import validate_xelon

from .models import TagXelon


class TagXelonForm(BSModalForm):
    class Meta:
        model = TagXelon
        fields = ['xelon', 'comments']
        widgets = {
            'xelon': forms.TextInput(attrs={'class': 'form-control col-sm-6'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        }

    def clean_xelon(self):
        data = self.cleaned_data['xelon']
        message = validate_xelon(data)
        if message:
            self.add_error('xelon', _(message))
        return data
