from django import forms
from django.utils.translation import ugettext as _
from bootstrap_modal_forms.forms import BSModalForm

from utils.django.validators import validate_vin, xml_parser
from .models import Corvet


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

    class Meta:
        model = Corvet
        fields = ['vin', 'xml_data']
        widgets = {
            'vin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Enter the VIN number")}),
        }

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
        if not data:
            self.add_error('xml_data', _('Invalid XML data'))
        return data

    def clean(self):
        cleaned_data = super(CorvetForm, self).clean()
        data = cleaned_data.get("xml_data")
        vin = cleaned_data.get("vin")
        if data and data['vin'] != vin:
            raise forms.ValidationError(
                _('XML data does not match VIN')
            )

    def save(self, commit=True):
        data = self.cleaned_data['xml_data']
        corvet = super(CorvetForm, self).save(commit=False)
        if data and commit:
            try:
                Corvet.objects.update_or_create(**data)
            except TypeError:
                raise forms.ValidationError(_('An internal error has occurred. Thank you recommend your request'))
        return corvet


class CorvetModalForm(BSModalForm):
    xml_data = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': _("Data in XML format available on the RepairNAV site during CORVET extraction..."),
                'rows': 10,
            }
        ),
        label=_('XML data'),
        required=True
    )

    class Meta:
        model = Corvet
        fields = '__all__'
        widgets = {
            'vin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Enter the VIN number")}),
        }

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
        if data:
            for field, value in data.items():
                self.cleaned_data[field] = value
        else:
            self.add_error('xml_data', _('Invalid XML data'))
        return data

    def clean(self):
        cleaned_data = super(CorvetModalForm, self).clean()
        data = cleaned_data.get("xml_data")
        vin = cleaned_data.get("vin")
        if data and data['vin'] != vin:
            raise forms.ValidationError(
                _('XML data does not match VIN')
            )
