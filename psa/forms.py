from django import forms
from django.utils.translation import ugettext as _

from utils.django.validators import validate_nac


class NacLicenseForm(forms.Form):
    SOFTWARES = [('001315031548167166', '7-3-1-r1_WAVE1'), ('001315031579159852', '21-08-25-12_NAC-r0_WAVE2')]

    software = forms.ChoiceField(
        label='Version Software', required=True, choices=SOFTWARES,
        widget=forms.Select(attrs={'class': 'custom-select form-control mx-sm-3 mb-2'})
    )
    uin = forms.CharField(
        label='V.I.N. ou UIN', required=True,
        widget=forms.TextInput(attrs={'class': 'form-control mx-sm-3 mb-2'})
    )

    def clean_uin(self):
        data = self.cleaned_data['uin']
        data, message = validate_nac(data)
        if message:
            raise forms.ValidationError(
                _(message),
                code='invalid',
                params={'value': data},
            )
        return data


class NacUpdateForm(forms.Form):
    SOFTWARES = [('001315031548167166', '7-3-1-r1_WAVE1'), ('001315031579159852', '21-08-25-12_NAC-r0_WAVE2'),
                 ('001315031576311163', '21-08-24-12_NAC-r1_WAVE2'), ('001315031563976162', '21-08-22-32_NAC-r1_WAVE2'),
                 ('001315031560945905', '21-07-67-32_NAC-r0_WAVE2'), ('001315031551279802', '21-07-67-32_NAC-r0_WAVE2'),
                 ('001315031524207679', '21-07-16-32_NAC-r0_WAVE2'), ('001315031511946541', '21-06-47-34_NAC-r0_WAVE2'),
                 ('001315031487843893', '21-05-68-24_NAC-r0_WAVE2'), ('001315031486085746', '21-04-62-54-R0_WAVE2'),
                 ('001315031475762081', '7-3-1-R0_WAVE1')]

    software = forms.ChoiceField(
        label='Version Software', required=True, choices=SOFTWARES,
        widget=forms.Select(attrs={'class': 'custom-select form-control mx-sm-3 mb-2'})
    )
