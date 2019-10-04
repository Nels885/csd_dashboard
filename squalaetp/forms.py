from django import forms
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError

import xml.etree.ElementTree as ET

import re


def validate_vin(value):
    """
    Function for the VIN validation
    :param value:
        VIN value
    :return:
        Error message if not valid
    """
    if not re.match(r'^VF[37]\w{14}$', str(value)):
        raise ValidationError(
            _('The V.I.N. is invalid, it should be 17 characters and be part of PSA vehicles'),
            code='invalid',
            params={'value': value},
        )


class CorvetForm(forms.Form):
    vin = forms.CharField(
        validators=[validate_vin],
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
