from django import forms
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from datetime import datetime
from bootstrap_modal_forms.forms import BSModalForm

import xml.etree.ElementTree as ET

from utils.django.validators import validate_vin
from .models import Corvet


class CorvetForm(forms.Form):
    vin = forms.CharField(
        max_length=17,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _("Enter the VIN number"),
            }
        ),
        required=True
    )
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

    def clean_vin(self):
        data = self.cleaned_data['vin']
        message = validate_vin(data)
        if message:
            raise ValidationError(
                _(message),
                code='invalid',
                params={'value': data},
            )
        return data

    def xml_parser(self, value):
        data = {"vin": ""}
        try:
            tree = ET.XML(self.cleaned_data[value])
            root = tree.getchildren()
            for list in root[1]:
                if list.tag == "DONNEES_VEHICULE":
                    for child in list:
                        if child.tag in ["WMI", "VDS", "VIS"]:
                            data['vin'] += child.text
                        elif child.tag in ["DATE_DEBUT_GARANTIE", "DATE_ENTREE_MONTAGE"]:
                            key, value = "DONNEE_{}".format(child.tag), child.text
                            if value:
                                data[key.lower()] = datetime.strptime(value, "%d/%m/%Y %H:%M:%S")
                        else:
                            key, value = "DONNEE_{}".format(child.tag), child.text
                            # print("{} : {}".format(key, value))
                            data[key.lower()] = value
                elif list.tag in ["LISTE_ATTRIBUTS", "LISTE_ELECTRONIQUES"]:
                    for child in list:
                        key, value = "{}_{}".format(child.tag, child.text[:3]), child.text[3:]
                        # print("{} : {}".format(key, value))
                        data[key.lower()] = value
                elif list.tag == "LISTE_ORGANES":
                    for child in list:
                        key, value = "{}s_{}".format(child.tag, child.text[:2]), child.text[2:]
                        # print("{} : {}".format(key, value))
                        data[key.lower()] = value
            if data['vin'] != self.cleaned_data['vin']:
                self.add_error('vin', _('XML data does not match VIN'))
                data = None
        except ET.ParseError:
            self.add_error('xml_data', _('Invalid XML data'))
            data = None
        return data


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
        fields = ['vin', 'xml_data']
        widgets = {
            'vin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Enter the VIN number")}),
        }

    def clean_vin(self):
        data = self.cleaned_data['vin']
        message = validate_vin(data)
        if message:
            raise ValidationError(
                _(message),
                code='invalid',
                params={'value': data},
            )
        return data

    def save(self, commit=True):
        xml_data = self.cleaned_data['xml_data']
        data = self.xml_parser(xml_data)
        tag = super(CorvetModalForm, self).save(commit=False)
        if data and commit:
            try:
                tag(**data)
                tag.save()
            except TypeError:
                raise ValidationError(_('An internal error has occurred. Thank you recommend your request'))
        return tag

    def xml_parser(self, value):
        data = {"vin": ""}
        try:
            tree = ET.XML(self.cleaned_data[value])
            root = tree.getchildren()
            for list in root[1]:
                if list.tag == "DONNEES_VEHICULE":
                    for child in list:
                        if child.tag in ["WMI", "VDS", "VIS"]:
                            data['vin'] += child.text
                        elif child.tag in ["DATE_DEBUT_GARANTIE", "DATE_ENTREE_MONTAGE"]:
                            key, value = "DONNEE_{}".format(child.tag), child.text
                            if value:
                                data[key.lower()] = datetime.strptime(value, "%d/%m/%Y %H:%M:%S")
                        else:
                            key, value = "DONNEE_{}".format(child.tag), child.text
                            # print("{} : {}".format(key, value))
                            data[key.lower()] = value
                elif list.tag in ["LISTE_ATTRIBUTS", "LISTE_ELECTRONIQUES"]:
                    for child in list:
                        key, value = "{}_{}".format(child.tag, child.text[:3]), child.text[3:]
                        # print("{} : {}".format(key, value))
                        data[key.lower()] = value
                elif list.tag == "LISTE_ORGANES":
                    for child in list:
                        key, value = "{}s_{}".format(child.tag, child.text[:2]), child.text[2:]
                        # print("{} : {}".format(key, value))
                        data[key.lower()] = value
            if data['vin'] != self.cleaned_data['vin']:
                self.add_error('vin', _('XML data does not match VIN'))
                data = None
        except (ET.ParseError, KeyError):
            self.add_error('xml_data', _('Invalid XML data'))
            data = None
        return data


class ExportCorvetForm(forms.Form):
    PRODUCTS = [('corvet', 'CORVET'), ('ecu', 'ECU'), ('bsi', 'BSI'), ('com200x', 'COM200x')]
    FORMATS = [('csv', 'CSV'), ('excel', 'EXCEL')]

    formats = forms.ChoiceField(
        label='Formats', required=False, choices=FORMATS,
        widget=forms.Select(attrs={'class': 'form-control mx-sm-3 mb-2'})
    )
    products = forms.ChoiceField(
        label='Produit', required=False, choices=PRODUCTS,
        widget=forms.Select(attrs={'class': 'form-control mx-sm-3 mb-2'}),
    )
