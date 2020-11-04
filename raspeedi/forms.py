from django.forms import ModelForm, TextInput, Select, CheckboxInput, Form, CharField
from django.utils.translation import ugettext as _
from crum import get_current_user

from utils.django.validators import validate_xelon
from .models import Raspeedi, UnlockProduct
from squalaetp.models import Xelon


class RaspeediForm(ModelForm):
    class Meta:
        model = Raspeedi
        fields = [
            'ref_boitier', 'produit', 'facade', 'type', 'dab', 'cam', 'dump_peedi',
            'cd_version', 'media', 'carto', 'dump_renesas', 'ref_mm', 'connecteur_ecran',
        ]
        widgets = {
            'ref_boitier': TextInput(attrs={'class': 'form-control', 'maxlength': 10}),
            'produit': Select(attrs={'class': 'form-control'}),
            'facade': TextInput(attrs={
                'class': 'form-control', 'pattern': '[A-Z0-9]+', 'style': 'text-transform: uppercase;'
            }),
            'type': Select(attrs={'class': 'form-control'}),
            'dab': CheckboxInput(attrs={'class': 'form-control'}),
            'cam': CheckboxInput(attrs={'class': 'form-control'}),
            'dump_peedi': TextInput(attrs={'class': 'form-control'}),
            'cd_version': TextInput(attrs={'class': 'form-control'}),
            'media': Select(attrs={'class': 'form-control'}),
            'carto': TextInput(attrs={'class': 'form-control'}),
            'dump_renesas': TextInput(attrs={'class': 'form-control'}),
            'ref_mm': TextInput(attrs={'class': 'form-control'}),
            'connecteur_ecran': Select(attrs={'class': 'form-control'}),
        }


class UnlockForm(Form):
    unlock = CharField(
        label='Numéro de dossier', max_length=10,
        widget=TextInput(attrs={'class': 'form-control mb-2 mr-sm-4', 'autofocus': ''})
    )

    def clean_unlock(self):
        data = self.cleaned_data['unlock']
        message = validate_xelon(data)
        if message:
            self.add_error('unlock', _(message))
        else:
            if UnlockProduct.objects.filter(unlock=Xelon.objects.get(numero_de_dossier=data), active=True):
                self.add_error('unlock', _('This Xelon number is already present for unlocking'))
        return data

    def save(self, commit=True):
        user = get_current_user()
        unlock = self.cleaned_data['unlock']
        instance = UnlockProduct.objects.create(user=user.userprofile,
                                                unlock=Xelon.objects.get(numero_de_dossier=unlock))
        if commit:
            instance.save()
        return instance
