from django import forms
from django.utils.translation import ugettext as _
from bootstrap_modal_forms.forms import BSModalForm

from utils.django.validators import validate_xelon

from .models import TagXelon, CsdSoftware


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


class SoftwareForm(forms.ModelForm):
    class Meta:
        model = CsdSoftware
        fields = [
            'jig', 'new_version', 'old_version', 'link_download', 'status', 'validation_date'
        ]
        widgets = {
            'jig': forms.TextInput(attrs={'class': 'form-control'}),
            'new_version': forms.TextInput(attrs={'class': 'form-control'}),
            'old_version': forms.TextInput(attrs={'class': 'form-control'}),
            'link_download': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'validation_date': forms.DateInput(attrs={'class': 'form-control'}),
        }
