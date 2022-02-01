from django import forms

FORMAT_CHOICES = [('xlsx', 'XLSX'), ('xls', 'XLS'), ('csv', 'CSV')]


class ExportCorvetForm(forms.Form):
    PRODUCTS = [
        ('corvet', '---'),
        ('ecu', 'ECU'), ('bsi', 'BSI'), ('com200x', 'COM200x'), ('bsm', 'BSM'), ('cvm', 'CVM'), ('dae', 'DAE'),
        ('emf', 'DISPLAY'), ('cmb', 'COMBINE'), ('nac', 'NAC'), ('rcc', 'RCC'), ('rtx', 'RTx'), ('rdx', 'RDx'),
        ('smeg', 'SMEG'), ('rneg', 'RNEG'), ('ng4', 'NG4'), ('icare', 'ICARE'), ('all', 'ALL'), ('xelon', 'ALL Xelon')
    ]
    COLS = [
        ('cmm', 'ECU'), ('bsi', 'BSI'), ('com200x', 'COM200x'), ('bsm', 'BSM'), ('cvm', 'CVM'), ('dae', 'DAE'),
        ('emf', 'DISPLAY'), ('cmb', 'COMBINE'), ('btel', 'NAV'), ('rad', 'RADIO')
    ]

    product = forms.ChoiceField(label='Produit', required=False, choices=PRODUCTS, widget=forms.Select())
    columns = forms.MultipleChoiceField(
        label='Sélect. col. Excel', required=False, choices=COLS, widget=forms.CheckboxSelectMultiple())
    formats = forms.ChoiceField(label='Formats', required=False, choices=FORMAT_CHOICES[:-1], widget=forms.Select())
    tag = forms.CharField(label="TAG Corvet", required=False)
    start_date = forms.DateField(
        label='Début date garantie', required=False, widget=forms.DateTimeInput(attrs={'placeholder': 'dd/mm/yyyy'}))
    end_date = forms.DateField(
        label='Fin date garantie', required=False, widget=forms.DateTimeInput(attrs={'placeholder': 'dd/mm/yyyy'}))


class ExportRemanForm(forms.Form):
    TABLES = [('batch', 'BATCH'), ('repair_reman', 'REPAIR'), ('base_ref_reman', 'BASE REF REMAN')]

    formats = forms.ChoiceField(label='Formats', required=False, choices=FORMAT_CHOICES[1:], widget=forms.Select())
    tables = forms.ChoiceField(label='Tableaux', required=False, choices=TABLES, widget=forms.Select())


class CorvetVinListForm(forms.Form):
    vin_list = forms.CharField(label='Liste de V.I.N.', required=True, widget=forms.Textarea())


class ExportToolsForm(forms.Form):
    TABLES = [('suptech', 'SUPTECH'), ('bga_time', 'UTILISATION BGA')]

    formats = forms.ChoiceField(label='Formats', required=False, choices=FORMAT_CHOICES[1:], widget=forms.Select())
    tables = forms.ChoiceField(label='Tableaux', required=False, choices=TABLES, widget=forms.Select())
