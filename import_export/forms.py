from django import forms


class ExportCorvetForm(forms.Form):
    PRODUCTS = [('corvet', 'ALL'), ('ecu', 'ECU'), ('bsi', 'BSI'), ('com', 'COM200x')]
    FORMATS = [('csv', 'CSV'), ('excel', 'EXCEL')]

    formats = forms.ChoiceField(
        label='Formats', required=False, choices=FORMATS,
        widget=forms.Select(attrs={'class': 'form-control mx-sm-3 mb-2'})
    )
    products = forms.ChoiceField(
        label='Produit', required=False, choices=PRODUCTS,
        widget=forms.Select(attrs={'class': 'form-control mx-sm-3 mb-2'}),
    )
