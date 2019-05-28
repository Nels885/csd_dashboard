from django import forms
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList

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


class ParaErrorList(ErrorList):

    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ''
        return '<div>%s</div>' % ''.join(['<p class="text-danger">* %s</p>' % e for e in self])


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
                'rows': 15,
            }
        ),
        required=True
    )
