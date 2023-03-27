from django import forms

# from .utils import CORVET_DICT
from squalaetp.models import Xelon
from reman.models import Batch
from psa.models import CorvetOption, CorvetChoices
from utils.django.forms.fields import ListTextWidget

FORMAT_CHOICES = [('xlsx', 'XLSX'), ('xls', 'XLS'), ('csv', 'CSV')]


class ExportCorvetForm(forms.Form):
    PRODUCTS = [
        ('corvet', '---'), ('btel', 'NAV'), ('rad', 'RADIO'), ('emf', 'DISPLAY'), ('cmb', 'COMBINE'),
        ('ecu', 'ECU'), ('bsi', 'BSI'), ('com200x', 'COM200x'), ('bsm', 'BSM'), ('cvm', 'CVM'), ('artiv', 'ARTIV'),
        ('dae', 'DAE'), ('abs_esp', 'ABS/ESP'), ('airbag', 'AIRBAG'), ('vmf', 'VMF'), ('dmtx', 'DMTX'),
        ('xelon', 'ALL Xelon')
    ]
    # COLS = [(key, key.upper()) for key in CORVET_DICT.keys()]
    COLS = [
        ('data_extra', 'Info Véhicule'), ('audio_cfg', 'Config Audio'),
        ('cmm', 'ECU'), ('cmm_extra', 'ECU Extra'), ('bsi', 'BSI'), ('bsi_extra', 'BSI Extra'), ('com200x', 'COM200x'),
        ('bsm', 'BSM'), ('cvm', 'CVM'), ('cvm_extra', 'CVM Extra'), ('artiv', 'ARTIV'), ('artiv_extra', 'ARTIV Extra'),
        ('dae', 'DAE'), ('abs_esp', 'ABS/ESP'), ('airbag', 'AIRBAG'), ('emf', 'DISPLAY'), ('vmf', 'VMF'),
        ('dmtx', 'DMTX'), ('dmtx_extra', 'DMTX Extra'),
        ('cmb', 'COMBINE'), ('btel', 'NAV'), ('btel_extra', 'NAV Extra'), ('rad', 'RADIO'), ('rad_extra', 'RADIO Extra')
    ]

    brand = forms.ChoiceField(label='Marque', required=False, choices=CorvetChoices.brands(), widget=forms.Select())
    vehicle = forms.ChoiceField(
        label='Véhicule (CORVET)', required=False, choices=CorvetChoices.vehicles(), widget=forms.Select())
    product = forms.ChoiceField(label='Type produit', required=False, choices=PRODUCTS, widget=forms.Select())
    hw_reference = forms.CharField(label="Réf. HW (CORVET)", required=False, widget=forms.TextInput())
    xelon_model = forms.CharField(label='Produit (XELON)', required=False, widget=forms.TextInput())
    xelon_vehicle = forms.CharField(label='Véhicule (XELON)', required=False, widget=forms.TextInput())
    vins = forms.CharField(label='Liste de V.I.N.', required=False, widget=forms.Textarea())
    columns = forms.MultipleChoiceField(
        label='Sélect. col. Excel', required=False, choices=COLS, widget=forms.CheckboxSelectMultiple())
    excel_type = forms.ChoiceField(label='Format', required=False, choices=FORMAT_CHOICES, widget=forms.Select())
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
        _tag_list = list(CorvetOption.objects.exclude(tag="").order_by('tag').values_list('tag').distinct())
        super().__init__(*args, **kwargs)
        self.fields['xelon_model'].widget = ListTextWidget(data_list=_model_list, name='model-list')
        self.fields['xelon_vehicle'].widget = ListTextWidget(data_list=_vehicle_list, name='vehicle-list')
        self.fields['tag'].widget = ListTextWidget(data_list=_tag_list, name='tag-list')


class ExportRemanForm(forms.Form):
    TABLES = [('batch', 'BATCH'), ('repair_reman', 'REPAIR'), ('base_ref_reman', 'BASE REF REMAN')]
    COLS = [
        # ('remanufacturing', 'Remise en neuf'),
        ('repair_parts', 'Pièces détachées'),
        # ('created', 'Créé par'), ('updated', 'Modifié par')
    ]
    TYPES = [('', '---'), ('etude', 'ETUDE'), ('repair', 'REPAIR')]

    customer = forms.CharField(label="Client", required=False, widget=forms.TextInput())
    batch_number = forms.CharField(label="N° de lot", required=False, widget=forms.TextInput())
    excel_type = forms.ChoiceField(label='Format', required=False, choices=FORMAT_CHOICES, widget=forms.Select())
    batch_type = forms.ChoiceField(label='Type de lot', required=False, choices=TYPES, widget=forms.Select())
    table = forms.ChoiceField(label='Tableaux', required=False, choices=TABLES, widget=forms.Select())
    columns = forms.MultipleChoiceField(
        label='Sélect. col. Excel', required=False, choices=COLS, widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        batchs = Batch.objects.exclude(customer="").order_by('customer')
        _customer_list = list(batchs.values_list('customer', flat=True).distinct())
        batchs = Batch.objects.exclude(batch_number="").order_by('batch_number')
        _batch_list = list(batchs.values_list('batch_number', flat=True).distinct())
        super().__init__(*args, **kwargs)
        self.fields['customer'].widget = ListTextWidget(data_list=_customer_list, name='customer-list')
        self.fields['batch_number'].widget = ListTextWidget(data_list=_batch_list, name='batch-list')


class CorvetVinListForm(forms.Form):
    vin_list = forms.CharField(label='Liste de V.I.N.', required=True, widget=forms.Textarea())
    corvet_tag = forms.CharField(label='TAG Corvet', required=False, widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        options = CorvetOption.objects.exclude(tag="").order_by('tag')
        _tag_list = list(options.values_list('tag', flat=True).distinct())
        super().__init__(*args, **kwargs)
        self.fields['corvet_tag'].widget = ListTextWidget(data_list=_tag_list, name='corvet-tag-list')


class ExportToolsForm(forms.Form):
    TABLES = [('suptech', 'SUPTECH'), ('bga_time', 'UTILISATION BGA')]
    MONTH_CHOICES = [('', 'All'), ('6', '6 derniers mois'), ('12', '12 derniers mois')]

    excel_type = forms.ChoiceField(label='Format', required=False, choices=FORMAT_CHOICES, widget=forms.Select())
    table = forms.ChoiceField(label='Tableaux', required=False, choices=TABLES, widget=forms.Select())
    date_delta = forms.ChoiceField(label='Date', required=False, choices=MONTH_CHOICES, widget=forms.Select())
