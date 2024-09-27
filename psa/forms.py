import re

from django import forms
from django.utils.translation import gettext_lazy as _
from bootstrap_modal_forms.forms import BSModalModelForm

from utils.scraping import xml_parser
from utils.django import is_ajax
from utils.django.validators import validate_vin, validate_nac
from utils.django.forms.fields import ListTextWidget
from .models import (
    Corvet, Firmware, Ecu, SupplierCode, Multimedia, CanRemote, Calibration, CalCurrent, ProductChoice
)
from .choices import PROD_CHOICES, ECU_TYPE_CHOICES, BTEL_PRODUCT_CHOICES, BTEL_TYPE_CHOICES, CAL_TYPE_CHOICES


class NacLicenseForm(forms.Form):
    software = forms.ModelChoiceField(
        queryset=Firmware.objects.filter(is_active=True), label='Version Software',
        required=True, widget=forms.Select()
    )
    uin = forms.CharField(label='V.I.N. ou UIN', required=True, widget=forms.TextInput())

    def clean_uin(self):
        data = self.cleaned_data['uin']
        data, error = validate_nac(data)
        if error:
            raise forms.ValidationError(error, code='invalid', params={'value': data})
        return data


class NacUpdateIdLicenseForm(forms.Form):
    update_id = forms.CharField(label='UpdateId', required=True, widget=forms.TextInput())
    uin = forms.CharField(label='V.I.N. ou UIN', required=True, widget=forms.TextInput())

    def clean_uin(self):
        data = self.cleaned_data['uin']
        data, error = validate_nac(data)
        if error:
            raise forms.ValidationError(error, code='invalid', params={'value': data})
        return data


class NacUpdateForm(forms.Form):
    software = forms.ModelChoiceField(
        queryset=Firmware.objects.all(), label='Version Software', required=True,
        widget=forms.Select(attrs={'class': 'custom-select form-control mx-sm-3 mb-2'})
    )


class CorvetForm(forms.ModelForm):
    xml_data = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': _("Data in XML format available on the RepairNAV site during CORVET extraction..."),
                'rows': 10,
            }
        ),
        required=True
    )
    vin = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': _("Enter the VIN number"), 'autofocus': ''}
        )
    )

    class Meta:
        model = Corvet
        fields = "__all__"

    def clean_vin(self):
        data = self.cleaned_data['vin']
        message = validate_vin(data)
        if message:
            raise forms.ValidationError(
                _(message),
                code='invalid',
                params={'value': data},
            )
        return data

    def clean_xml_data(self):
        xml_data = self.cleaned_data['xml_data']
        data = xml_parser(xml_data)
        vin = self.cleaned_data.get("vin")
        if isinstance(data, dict):
            if data.get('vin') == vin and data.get('donnee_date_entree_montage'):
                for field, value in data.items():
                    self.cleaned_data[field] = value
            elif data.get('vin') != vin:
                self.add_error('xml_data', _('XML data does not match VIN'))
        else:
            self.add_error('xml_data', _('Invalid XML data'))
        return data

    def clean(self):
        cleaned_data = super(CorvetForm, self).clean()
        data = cleaned_data.get('xml_data')
        if isinstance(data, dict) and not data.get('donnee_date_entree_montage'):
            raise forms.ValidationError(_('VIN error !'))


class CorvetModalForm(CorvetForm, BSModalModelForm):

    class Meta(CorvetForm):
        model = Corvet
        fields = '__all__'

    def save(self, commit=True):
        instance = super(CorvetModalForm, self).save(commit=False)
        if commit and not is_ajax(self.request):
            instance.save()
        return instance


class ProductChoiceAdminForm(forms.ModelForm):
    TYPE_CHOICES = [('', '---')] + BTEL_TYPE_CHOICES + ECU_TYPE_CHOICES

    ecu_type = forms.ChoiceField(label='Type ECU', choices=TYPE_CHOICES)
    cal_attribute = forms.ChoiceField(label='Attribut CAL', choices=CAL_TYPE_CHOICES)

    class Meta:
        model = ProductChoice
        fields = '__all__'


class EcuAdminForm(forms.ModelForm):
    type = forms.ChoiceField(choices=[('', '---')] + ECU_TYPE_CHOICES)

    class Meta:
        model = Ecu
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        suppliers = SupplierCode.objects.all()
        _supplier_list = list(suppliers.values_list('name', flat=True).distinct())
        super().__init__(*args, **kwargs)
        self.fields['supplier_oe'].widget = ListTextWidget(data_list=_supplier_list, name='supplier-list')


class CalibrationAdminForm(forms.ModelForm):
    type = forms.ChoiceField(choices=CAL_TYPE_CHOICES)

    class Meta:
        model = Calibration
        fields = '__all__'


class CalCurrentAdminForm(forms.ModelForm):
    type = forms.ChoiceField(choices=CAL_TYPE_CHOICES)

    class Meta:
        model = CalCurrent
        fields = '__all__'


class FirmwareAdminForm(forms.ModelForm):
    FW_TYPE_CHOICES = [
        ('', '---'),
        ('NAC_EUR_WAVE2', 'NAC_EUR_WAVE2'),
        ('NAC_EUR_WAVE1', 'NAC_EUR_WAVE1'),
        ('NAC_EUR_WAVE3', 'NAC_EUR_WAVE3'),
        ('NAC_EUR_WAVE4', 'NAV_EUR_WAVE4'),
        ('RCC_EU_W2', 'RCC_EU_W2'),
        ('RCC_EU_W3_ECO', 'RCC_EU_W3_ECO')
    ]

    ecu_type = forms.ChoiceField(label='EcuType', choices=FW_TYPE_CHOICES)

    class Meta:
        model = Firmware
        fields = '__all__'


class MultimediaAdminForm(forms.ModelForm):
    name = forms.ChoiceField(choices=[('', '---')] + BTEL_PRODUCT_CHOICES)
    type = forms.ChoiceField(choices=[('', '---')] + BTEL_TYPE_CHOICES)

    class Meta:
        model = Multimedia
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        _supplier_list = self._data_list(SupplierCode, 'name')
        _nand_list = self._data_list(Multimedia, 'flash_nand')
        _emmc_list = self._data_list(Multimedia, 'emmc')
        super().__init__(*args, **kwargs)
        self.fields['supplier_oe'].widget = ListTextWidget(data_list=_supplier_list, name='supplier-list')
        self.fields['emmc'].widget = ListTextWidget(data_list=_emmc_list, name='emmc-list')
        self.fields['flash_nand'].widget = ListTextWidget(data_list=_nand_list, name='nand-list')

    def _data_list(self, model, field):
        queryset = model.objects.all()
        return list(queryset.exclude(**{field: ''}).order_by(field).values_list(field, flat=True).distinct())


class CanRemoteAdminForm(forms.ModelForm):
    NEW_LABELS = [
        "VOL+", "VOL-", "EJECT", "MODE", "DARK", "SOURCE", "TA/INFO", "UP", "DOWN", "SEEK-UP", "SEEK-DWN", "LIST",
        "AUDIO", "BAND", "ESC", "M1", "M2", "M3", "M4", "M5", "M6", "MUTE", "TEL_V", "TEL_R", "BACK", "NAV", "RADIO",
        "SETUP", "ADDR BOOK", "MEDIA", "TRAFFIC", "JOY_ENT", "JOY_ROTR", "JOY-ROTL", "JOY_UP", "JOY_RIGHT", "JOY_DWN",
        "JOY_LEFT", "DRIVE", "WEB", "CLIM"
    ]
    LABELS = [
        'AUDIO', 'BACK', 'BAND', 'CLIM', 'DARK', 'DRIVE', 'DOWN', 'EJECT', 'ESC', 'LIST', 'M1', 'M2', 'M3', 'M4', 'M5',
        'M6', 'MEDIA', 'MENU', 'MODE', 'MUTE', 'NAV', 'RADIO', 'SEEK-UP', 'SEEK-DWN', 'SETUP', 'SOURCE', 'TA/INFO',
        'TEL', 'TRAFFIC', 'UP', 'VOL+', 'VOL-', 'WEB'
    ]
    CAN_IDS = ['0x122', '0x21F']
    CMD_CHOICES = [('FMUX', 'FMUX'), ('VMF', 'Cmd Volant'), ('DSGN', 'Cmd Joystick'), ('TEST', 'TEST')]

    type = forms.ChoiceField(choices=CMD_CHOICES)
    product = forms.ChoiceField(choices=PROD_CHOICES, required=False)
    location = forms.IntegerField(required=False)

    class Meta:
        model = CanRemote
        exclude = ['corvets']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['label'].widget = ListTextWidget(data_list=self.NEW_LABELS, name='label-list')
        self.fields['can_id'].widget = ListTextWidget(data_list=self.CAN_IDS, name='canid-list')

    def clean_location(self):
        data = self.cleaned_data['location']
        if not data:
            labels_dict = dict((key, value) for value, key in enumerate(self.NEW_LABELS, 1))
            return labels_dict.get(self.cleaned_data['label'], 0)
        return data

    def clean_can_id(self):
        data = self.cleaned_data['can_id'].replace("0x", "")
        if not data.isdigit():
            try:
                int(data, 16)
            except ValueError:
                self.add_error('can_id', "uniquement des nombres")
        data = f"0x{data}"
        return data

    def clean_data(self):
        data = self.cleaned_data['data']
        if re.match(r'^B[0-7].\d{2}$', str(data)):
            return data
        data_list = []
        for value in data.split(','):
            value = value.replace("0x", "")
            if not value.isdigit():
                try:
                    int(value, 16)
                except ValueError:
                    self.add_error('data', "Erreur de format")
                    data_list = []
                    break
            data_list.append(f"0x{value}")
        return ",".join(data_list)


class SelectCanRemoteForm(forms.Form):
    product = forms.ChoiceField(label="Produit", choices=PROD_CHOICES, required=False)
    vehicle = forms.CharField(label='Véhicule', max_length=200, required=True)

    def __init__(self, *args, **kwargs):
        remotes = CanRemote.objects.exclude(vehicles__name__exact='').order_by('vehicles__name')
        _vehicle_list = list(remotes.values_list('vehicles__name', flat=True).distinct())
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].widget = ListTextWidget(data_list=_vehicle_list, name='vehicle')
