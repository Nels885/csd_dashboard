from django import forms

from utils.django.validators import validate_nac

from .models import Firmware


class NacLicenseForm(forms.Form):
    software = forms.ModelChoiceField(
        queryset=Firmware.objects.filter(is_active=True), label='Version Software',
        required=True, widget=forms.Select(attrs={'class': 'custom-select form-control mx-sm-3 mb-2'})
    )
    uin = forms.CharField(
        label='V.I.N. ou UIN', required=True,
        widget=forms.TextInput(attrs={'class': 'form-control mx-sm-3 mb-2'})
    )

    def clean_uin(self):
        data = self.cleaned_data['uin']
        data, error = validate_nac(data)
        if error:
            raise forms.ValidationError(error, code='invalid', params={'value': data})
        return data


class NacUpdateForm(forms.Form):
    software = forms.ModelChoiceField(
        queryset=Firmware.objects.all(), label='Version Software', required=True,
        widget=forms.Select(attrs={'class': 'custom-select form-control mx-sm-3 mb-2'})
    )
