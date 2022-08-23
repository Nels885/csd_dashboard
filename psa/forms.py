from django import forms
from django.utils.translation import gettext as _
from bootstrap_modal_forms.forms import BSModalModelForm

from utils.django.validators import validate_vin, validate_nac, xml_parser
from .models import Corvet, Firmware


class NacLicenseForm(forms.Form):
    software = forms.ModelChoiceField(
        queryset=Firmware.objects.filter(is_active=True), label='Version Software',
        required=True, widget=forms.Select()
    )
    uin = forms.CharField(label='V.I.N. ou UIN', required=True, widget=forms.TextInput())

    def clean_uin(self):
        data = self.cleaned_data['uin']
        data, error = validate_nac(data)
        if error:
            raise forms.ValidationError(error, code='invalid', params={'value': data})
        return data


class NacUpdateIdLicenseForm(forms.Form):
    update_id = forms.CharField(label='UpdateId', required=True, widget=forms.TextInput())
    uin = forms.CharField(label='V.I.N. ou UIN', required=True, widget=forms.TextInput())

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


class CorvetForm(forms.ModelForm):
    xml_data = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': _("Data in XML format available on the RepairNAV site during CORVET extraction..."),
                'rows': 10,
            }
        ),
        required=True
    )
    vin = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': _("Enter the VIN number"), 'autofocus': ''}
        )
    )

    class Meta:
        model = Corvet
        fields = "__all__"

    def clean_vin(self):
        data = self.cleaned_data['vin']
        message = validate_vin(data)
        if message:
            raise forms.ValidationError(
                _(message),
                code='invalid',
                params={'value': data},
            )
        return data

    def clean_xml_data(self):
        xml_data = self.cleaned_data['xml_data']
        data = xml_parser(xml_data)
        vin = self.cleaned_data.get("vin")
        if isinstance(data, dict):
            if data.get('vin') == vin and data.get('donnee_date_entree_montage'):
                for field, value in data.items():
                    self.cleaned_data[field] = value
            elif data.get('vin') != vin:
                self.add_error('xml_data', _('XML data does not match VIN'))
        else:
            self.add_error('xml_data', _('Invalid XML data'))
        return data

    def clean(self):
        cleaned_data = super(CorvetForm, self).clean()
        data = cleaned_data.get('xml_data')
        if isinstance(data, dict) and not data.get('donnee_date_entree_montage'):
            raise forms.ValidationError(_('VIN error !'))


class CorvetModalForm(CorvetForm, BSModalModelForm):

    class Meta(CorvetForm):
        model = Corvet
        fields = '__all__'

    def save(self, commit=True):
        instance = super(CorvetModalForm, self).save(commit=False)
        if commit and not self.request.is_ajax():
            instance.save()
        return instance
