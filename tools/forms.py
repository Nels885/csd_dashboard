from django import forms
from django.utils.translation import ugettext as _
from bootstrap_modal_forms.forms import BSModalModelForm

from utils.django.validators import validate_xelon

from .models import TagXelon, CsdSoftware, ThermalChamber


class TagXelonForm(BSModalModelForm):
    class Meta:
        model = TagXelon
        fields = ['xelon', 'comments']
        widgets = {
            'xelon': forms.TextInput(
                attrs={'class': 'form-control col-sm-6'}    # 'onkeypress': 'return event.keyCode != 13;'
            ),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        }

    def __init__(self, *args, **kwargs):
        super(TagXelonForm, self).__init__(*args, **kwargs)
        self.fields['comments'].initial = 'RAS OK'

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


class ThermalFrom(forms.ModelForm):
    class Meta:
        model = ThermalChamber
        fields = ['operating_mode', 'xelon_number']
        widgets = {
            'operating_mode': forms.Select(attrs={'class': 'custom-select form-control'}),
            'xelon_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
