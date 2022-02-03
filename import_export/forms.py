from django import forms

from squalaetp.models import Xelon
from utils.django.forms.fields import ListTextWidget

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

    xelon_model = forms.CharField(label='Modèle (XELON)', required=False, widget=forms.TextInput())
    xelon_vehicle = forms.CharField(label='Véhicule (XELON)', required=False, widget=forms.TextInput())
    product = forms.ChoiceField(label='Type produit', required=False, choices=PRODUCTS, widget=forms.Select())
    columns = forms.MultipleChoiceField(
        label='Sélect. col. Excel', required=False, choices=COLS, widget=forms.CheckboxSelectMultiple())
    formats = forms.ChoiceField(label='Formats', required=False, choices=FORMAT_CHOICES[:-1], widget=forms.Select())
    tag = forms.CharField(label="TAG Corvet", required=False, widget=forms.TextInput())
    start_date = forms.DateField(
        label='Début date garantie', required=False, widget=forms.DateTimeInput(attrs={'placeholder': 'dd/mm/yyyy'}))
    end_date = forms.DateField(
        label='Fin date garantie', required=False, widget=forms.DateTimeInput(attrs={'placeholder': 'dd/mm/yyyy'}))

    def __init__(self, *args, **kwargs):
        xelons = Xelon.objects.exclude(modele_produit="").order_by('modele_produit')
        _model_list = list(xelons.values_list('modele_produit', flat=True).distinct())
        xelons = Xelon.objects.exclude(modele_vehicule="").order_by('modele_vehicule')
        _vehicle_list = list(xelons.values_list('modele_vehicule', flat=True).distinct())
        super().__init__(*args, **kwargs)
        self.fields['xelon_model'].widget = ListTextWidget(data_list=_model_list, name='model-list')
        self.fields['xelon_vehicle'].widget = ListTextWidget(data_list=_vehicle_list, name='vehicle-list')


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
