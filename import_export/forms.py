from django import forms

FORMAT_CHOICES = [('csv', 'CSV'), ('xls', 'XLS'), ('xlsx', 'XLSX')]


class ExportCorvetForm(forms.Form):
    PRODUCTS = [
        ('ecu', 'ECU'), ('bsi', 'BSI'), ('com200x', 'COM200x'), ('bsm', 'BSM'), ('nac', 'NAC'), ('rtx', 'RTx'),
        ('smeg', 'SMEG'), ('rneg', 'RNEG'), ('ng4', 'NG4')
    ]

    formats = forms.ChoiceField(label='Formats', required=False, choices=FORMAT_CHOICES[1:], widget=forms.Select())
    products = forms.ChoiceField(label='Produit', required=False, choices=PRODUCTS, widget=forms.Select())


class ExportRemanForm(forms.Form):
    TABLES = [('batch', 'BATCH'), ('repair_reman', 'REPAIR'), ('base_ref_reman', 'BASE REF REMAN')]

    formats = forms.ChoiceField(label='Formats', required=False, choices=FORMAT_CHOICES[1:], widget=forms.Select())
    tables = forms.ChoiceField(label='Tableaux', required=False, choices=TABLES, widget=forms.Select())


class ExportCorvetVinListForm(forms.Form):
    vin_list = forms.CharField(label='Liste de V.I.N.', required=True, widget=forms.Textarea())


class ExportToolsForm(forms.Form):
    TABLES = [('suptech', 'SUPTECH'), ('bga_time', 'UTILISATION BGA')]

    formats = forms.ChoiceField(label='Formats', required=False, choices=FORMAT_CHOICES[1:], widget=forms.Select())
    tables = forms.ChoiceField(label='Tableaux', required=False, choices=TABLES, widget=forms.Select())
