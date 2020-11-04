from django import forms
from django.utils.translation import ugettext as _
from bootstrap_modal_forms.forms import BSModalModelForm

from utils.django.validators import validate_vin, xml_parser
from utils.file.export import xml_corvet_file
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
        fields = "__all__"
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
        vin = self.cleaned_data.get("vin")
        if data and data['vin'] == vin:
            for field, value in data.items():
                self.cleaned_data[field] = value
            xml_corvet_file(xml_data, vin)
        elif data and data['vin'] != vin:
            self.add_error('xml_data', _('XML data does not match VIN'))
        else:
            self.add_error('xml_data', _('Invalid XML data'))
        return xml_data

    # def clean(self):
    #     cleaned_data = super(CorvetForm, self).clean()
    #     xml_data = cleaned_data.get("xml_data")
    #     data = xml_parser(xml_data)
    #     vin = cleaned_data.get("vin")
    #     if data and data['vin'] != vin:
    #         raise forms.ValidationError(
    #             _('XML data does not match VIN')
    #         )
    #     else:
    #         xml_corvet_file(xml_data, vin)

    # def save(self, commit=True):
    #     data = xml_parser(self.cleaned_data['xml_data'])
    #     corvet = super(CorvetForm, self).save(commit=False)
    #     if commit:
    #         corvet.save()
    #     # if data and commit:
    #     #     try:
    #     #         Corvet.objects.update_or_create(vin=data.pop("vin"), defaults=data)
    #     #     except TypeError:
    #     #         raise forms.ValidationError(_('An internal error has occurred. Thank you recommend your request'))
    #     return corvet


class CorvetModalForm(CorvetForm, BSModalModelForm):

    class Meta(CorvetForm):
        model = Corvet
        fields = '__all__'
        widgets = {
            'vin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Enter the VIN number")}),
        }

    # def clean_xml_data(self):
    #     xml_data = self.cleaned_data['xml_data']
    #     data = xml_parser(xml_data)
    #     if data:
    #         for field, value in data.items():
    #             self.cleaned_data[field] = value
    #     else:
    #         self.add_error('xml_data', _('Invalid XML data'))
    #     return xml_data
    #
    # def clean(self):
    #     cleaned_data = super(CorvetForm, self).clean()
    #     xml_data = cleaned_data.get("xml_data")
    #     data = xml_parser(xml_data)
    #     vin = cleaned_data.get("vin")
    #     if data and data['vin'] != vin:
    #         raise forms.ValidationError(
    #             _('XML data does not match VIN')
    #         )
    #     else:
    #         xml_corvet_file(xml_data, vin)
