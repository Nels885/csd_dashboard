from django.forms import ModelForm, TextInput, Select, CheckboxInput

from .models import Raspeedi


class RaspeediForm(ModelForm):
    class Meta:
        model = Raspeedi
        fields = [
            'ref_boitier', 'produit', 'facade', 'type', 'dab', 'cam', 'dump_peedi',
            'cd_version', 'media', 'carto', 'dump_renesas', 'ref_mm', 'connecteur_ecran',
        ]
        widgets = {
            'ref_boitier': TextInput(attrs={'class': 'form-control'}),
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
