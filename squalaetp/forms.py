from django import forms

from psa.models import Corvet


class IhmModalForm(forms.ModelForm):
    vin = forms.CharField(label="V.I.N. (XELON)")
    modele_produit = forms.CharField(label="Modèle produit (XELON)")
    modele_vehicule = forms.CharField(label="Modèle véhicule (XELON)")

    class Meta:
        model = Corvet
        fields = [
            'vin', 'modele_produit', 'modele_vehicule',
            'electronique_14x', 'electronique_94x', 'electronique_44x',
            'electronique_14f', 'electronique_94f', 'electronique_44f',
        ]

    def __init__(self, *args, **kwargs):
        super(IhmModalForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance:
            for field in self.fields:
                self.fields[field].widget.attrs['readonly'] = True
                # self.fields[field].widget.attrs['style'] = 'width: 50%;'
