from django import forms
from django.utils.translation import gettext as _
from django.template.loader import render_to_string
from django.contrib.admin.widgets import FilteredSelectMultiple
from bootstrap_modal_forms.forms import BSModalModelForm, BSModalForm
from constance import config

from utils.scraping import xml_parser, xml_sivin_parser
from utils.django.validators import validate_vin, vin_psa_isvalid
from utils.file.export import xml_corvet_file
from utils.conf import string_to_list
from psa.models import Corvet, Multimedia, Ecu
from .models import Xelon, Action, Sivin, ProductCode, ProductCategory, XelonTemporary
from .tasks import send_email_task
from utils.django import is_ajax
from utils.django.forms.fields import ListTextWidget
from utils.django.models import defaults_dict
from utils.file import LogFile
from utils.conf import CSD_ROOT


class IhmEmailModalForm(BSModalForm):
    to = forms.CharField(label='À', required=True, widget=forms.TextInput())
    cc = forms.CharField(label='Cc', widget=forms.TextInput())
    subject = forms.CharField(label='Objet', required=True, widget=forms.TextInput())
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 10}), required=True)

    def __init__(self, *args, **kwargs):
        super(IhmEmailModalForm, self).__init__(*args, **kwargs)
        cc_email_list = config.CSD_CC_EMAIL_LIST
        if self.request.user.email not in cc_email_list:
            cc_email_list = f"{self.request.user.email}; {cc_email_list}"
        self.fields['cc'].initial = cc_email_list

    def send_email(self):
        send_email_task.delay(
            subject=self.cleaned_data['subject'], body=self.cleaned_data['message'], from_email=self.request.user.email,
            to=string_to_list(self.cleaned_data['to']), cc=string_to_list(self.cleaned_data['cc'])
        )

    @staticmethod
    def vin_message(model, request):
        domain = config.WEBSITE_DOMAIN
        queryset = model.actions.filter(content__contains="OLD_VIN")
        rasp_log = LogFile(CSD_ROOT).vin_err_filter(model.modele_produit, model.numero_de_dossier)
        if queryset:
            data = queryset.first().content.split('\n')
            vins = {"old_vin": data[0][-17:], "new_vin": data[1][-17:]}
        else:
            vins = None
        message = render_to_string('squalaetp/email_format/vin_error_email.html', locals())
        return message

    @staticmethod
    def prod_message(model, request):
        domain = config.WEBSITE_DOMAIN
        queryset = model.actions.filter(content__contains="OLD_PROD")
        if queryset:
            data = queryset.first().content.split('\n')
            prods = {"old_prod": data[0][9:], "new_prod": data[1][9:]}
        else:
            prods = None
        message = render_to_string('squalaetp/email_format/prod_error_email.html', locals())
        return message

    @staticmethod
    def adm_message(model, request):
        domain = config.WEBSITE_DOMAIN
        if request.GET.get("select") == "prod":
            select = "modèle produit"
        else:
            select = "V.I.N."
        message = render_to_string('squalaetp/email_format/adm_email.html', locals())
        return message


class VinCorvetModalForm(BSModalModelForm):
    xml_data = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': _("Data in XML format available on the RepairNAV site during CORVET extraction..."),
                'rows': 10,
            }
        ),
        required=False
    )
    force_vin = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = Xelon
        fields = ['vin']
        widgets = {
            'vin': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': _("Enter the VIN number"), 'autofocus': ''}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(VinCorvetModalForm, self).__init__(*args, **kwargs)
        self.oldVin = self.instance.vin

    def clean_vin(self):
        data = self.cleaned_data['vin']
        message = validate_vin(data, psa_type=False)
        if message:
            raise forms.ValidationError(_(message), code='invalid', params={'value': data})
        return data

    def clean_xml_data(self):
        xml_data = self.cleaned_data['xml_data']
        if xml_data:
            data = xml_parser(xml_data)
            no_fields = ['vin', 'btel', 'radio', 'bsi', 'emf', 'cmm', 'bsm']
            all_data = {key: '' for key in [f.name for f in Corvet._meta.local_fields if f.name not in no_fields]}
            all_data.update({'donnee_date_debut_garantie': None, 'donnee_date_entree_montage': None})
            vin = self.cleaned_data.get("vin")
            if isinstance(data, dict):
                all_data.update(data)
                if data.get('vin') == vin and data.get('donnee_date_entree_montage'):
                    if is_ajax(self.request):
                        xml_corvet_file(self.instance, xml_data, vin)
                if data.get('vin') != vin:
                    self.add_error('xml_data', _('XML data does not match VIN'))
            else:
                self.add_error('xml_data', _('Invalid XML data'))
                all_data = data
            return all_data
        return xml_data

    def clean(self):
        cleaned_data = super(VinCorvetModalForm, self).clean()
        vin = cleaned_data.get('vin')
        data = cleaned_data.get('xml_data')
        print(cleaned_data.get('force_vin'), type(cleaned_data.get('force_vin')))
        if not cleaned_data.get('force_vin'):
            if vin and isinstance(data, dict) and not data.get('donnee_date_entree_montage'):
                raise forms.ValidationError(_('VIN error !'))
            elif vin != self.oldVin and vin_psa_isvalid(vin) and not isinstance(data, dict):
                if not Corvet.objects.filter(vin=vin):
                    raise forms.ValidationError(_('New PSA VIN, please use the Import CORVET button !'))

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit and not is_ajax(self.request):
            data = self.cleaned_data['xml_data']
            vin = self.cleaned_data['vin']
            if data and vin:
                defaults = defaults_dict(Corvet, data, 'vin')
                Corvet.objects.update_or_create(vin=vin, defaults=defaults)
            if vin != self.oldVin:
                content = "OLD_VIN: {}\nNEW_VIN: {}".format(self.oldVin, vin)
                Action.objects.create(content=content, content_object=self.instance)
            instance.save()
        return instance


class ProductModalForm(BSModalModelForm):
    class Meta:
        model = Xelon
        fields = ['modele_produit', 'modele_vehicule']
        widgets = {'modele_vehicule': forms.TextInput(attrs={'readonly': True})}

    def __init__(self, *args, **kwargs):
        products = ProductCategory.objects.exclude(product_model="").order_by('product_model')
        self.data_list = list(products.values_list('product_model', flat=True).distinct())
        super(ProductModalForm, self).__init__(*args, **kwargs)
        self.fields['modele_produit'].widget = ListTextWidget(data_list=self.data_list, name='value-list')
        self.fields['modele_produit'].required = True
        self.oldProduct = self.instance.modele_produit
        self.oldVehicle = self.instance.modele_vehicule

    def clean_modele_produit(self):
        data = self.cleaned_data['modele_produit']
        if data not in self.data_list:
            self.add_error('modele_produit', _('Xelon product model does not exist !'))
        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit and not is_ajax(self.request):
            product = self.cleaned_data['modele_produit']
            vehicle = self.cleaned_data['modele_vehicule']
            if product and vehicle and not is_ajax(self.request):
                if product != self.oldProduct:
                    content = "OLD_PROD: {}\nNEW_PROD: {}".format(self.oldProduct, product)
                    Action.objects.create(content=content, content_object=self.instance)
                if vehicle != self.oldVehicle:
                    content = "OLD_VEH: {}\nNEW_VEH: {}".format(self.oldProduct, vehicle)
                    Action.objects.create(content=content, content_object=self.instance)
            instance.save()
        return instance


class NewSerialNumberModalForm(BSModalModelForm):
    class Meta:
        model = Xelon
        fields = ['new_sn']

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit and not is_ajax(self.request):
            new_sr = self.cleaned_data['new_sn']
            content = f"NEW_SN: {new_sr}"
            instance.actions.create(content=content)
            instance.save()
        return instance


class SivinModalForm(BSModalModelForm):
    immat_siv = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': _("Enter the IMMAT number"), 'autofocus': ''}
        )
    )
    xml_data = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': _("Data in XML format available on the RepairNAV site during SIVIN extraction..."),
                'rows': 10,
            }
        ),
        required=True
    )

    class Meta:
        model = Sivin
        exclude = ["corvet"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['codif_vin'].required = False

    def clean_xml_data(self):
        xml_data = self.cleaned_data['xml_data']
        immat_siv = self.cleaned_data.get('immat_siv', '').upper()
        data = xml_sivin_parser(xml_data)
        if isinstance(data, dict):
            if data.get('immat_siv') == immat_siv:
                for field, value in data.items():
                    self.cleaned_data[field] = value
                return xml_data
            self.add_error('xml_data', _('XML data does not match IMMAT'))
        else:
            self.add_error('xml_data', _('Invalid XML data'))
        return xml_data

    def save(self, commit=True):
        del self.fields['xml_data']
        instance = super().save(commit=False)
        if commit and not is_ajax(self.request):
            instance.save()
        return instance


class ProductCodeAdminForm(forms.ModelForm):
    medias = forms.ModelMultipleChoiceField(
        queryset=Multimedia.objects.all(), widget=FilteredSelectMultiple("Multimedia", is_stacked=False),
        required=False)
    ecus = forms.ModelMultipleChoiceField(
        queryset=Ecu.objects.all(), widget=FilteredSelectMultiple("Ecu", is_stacked=False), required=False)

    class Meta:
        model = ProductCode
        fields = ['name', 'medias', 'ecus']


class XelonCloseModalForm(BSModalModelForm):

    class Meta:
        model = Xelon
        fields = ['type_de_cloture']

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit and not is_ajax(self.request):
            instance.type_de_cloture = "N/A"
            instance.save()
            Action.objects.create(content="Dossier en retard => FAIT", content_object=instance)
        return instance


class XelonTemporaryForm(forms.ModelForm):

    class Meta:
        model = XelonTemporary
        exclude = ('created_by', 'corvet')

    def __init__(self, *args, **kwargs):
        products = ProductCategory.objects.exclude(product_model="").order_by('product_model')
        vehicles = Xelon.objects.exclude(modele_vehicule="").order_by('modele_vehicule')
        prod_list = list(products.values_list('product_model', flat=True).distinct())
        vehicle_list = list(vehicles.values_list('modele_vehicule', flat=True).distinct())
        super().__init__(*args, **kwargs)
        self.fields['modele_produit'].widget = ListTextWidget(data_list=prod_list, name='prod-list')
        self.fields['modele_vehicule'].widget = ListTextWidget(data_list=vehicle_list, name='vehicle-list')


class XelonTemporaryModalForm(XelonTemporaryForm, BSModalModelForm):

    def __init_(self, *args, **kwargs):
        super().__init(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit and not is_ajax(self.request):
            instance.type_de_cloture = "N/A"
            instance.save()
            Action.objects.create(content="Dossier en retard => FAIT", content_object=instance)
        return instance
