from django import forms

FORMAT_CHOICES = [('csv', 'CSV'), ('xls', 'XLS'), ('xlsx', 'XLSX')]


class ExportCorvetForm(forms.Form):
    PRODUCTS = [
        ('corvet', 'ALL'), ('ecu', 'ECU'), ('bsi', 'BSI'), ('com200x', 'COM200x'), ('bsm', 'BSM'),
        ('nac', 'NAC')
    ]

    formats = forms.ChoiceField(
        label='Formats', required=False, choices=FORMAT_CHOICES,
        widget=forms.Select(attrs={'style': 'width:100px', 'class': 'custom-select form-control mx-sm-3 mb-2'})
    )
    products = forms.ChoiceField(
        label='Produit', required=False, choices=PRODUCTS,
        widget=forms.Select(attrs={'style': 'width:100px', 'class': 'custom-select form-control mx-sm-3 mb-2'}),
    )


class ExportRemanForm(forms.Form):
    TABLES = [('batch', 'BATCH'), ('repair_reman', 'REPAIR'), ('base_ref_reman', 'BASE REF REMAN')]

    formats = forms.ChoiceField(
        label='Formats', required=False, choices=FORMAT_CHOICES,
        widget=forms.Select(attrs={'style': 'width:100px', 'class': 'custom-select form-control mx-sm-3 mb-2'})
    )
    tables = forms.ChoiceField(
        label='Tableaux', required=False, choices=TABLES,
        widget=forms.Select(attrs={'style': 'width:200px', 'class': 'custom-select form-control mx-sm-3 mb-2'}),
    )


class ExportCorvetVinListForm(forms.Form):
    vin_list = forms.CharField(
        label='Liste de V.I.N.', required=True,
        widget=forms.Textarea(attrs={'class': 'form-control mx-sm-3 mb-2', 'rows': 8}),
    )
