from django import forms
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from bootstrap_modal_forms.forms import BSModalModelForm, BSModalForm
from constance import config

from utils.django.validators import validate_vin, xml_parser
from utils.file.export import xml_corvet_file
from utils.conf import string_to_list
from psa.models import Corvet
from .models import Xelon, Action
from .tasks import send_email_task
from utils.django.forms.fields import ListTextWidget


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
        self.fields['to'].initial = config.CHANGE_VIN_TO_EMAIL_LIST
        self.fields['cc'].initial = cc_email_list

    def send_email(self):
        send_email_task.delay(
            subject=self.cleaned_data['subject'], body=self.cleaned_data['message'], from_email=self.request.user.email,
            to=string_to_list(self.cleaned_data['to']), cc=string_to_list(self.cleaned_data['cc'])
        )

    @staticmethod
    def vin_message(model, request):
        queryset = model.actions.filter(content__contains="OLD_VIN")
        if queryset:
            data = queryset.first().content.split('\n')
            vins = {"old_vin": data[0][-17:], "new_vin": data[1][-17:]}
        else:
            vins = None
        message = render_to_string('squalaetp/email_format/vin_error_email.html', locals())
        return message

    @staticmethod
    def prod_message(model, request):
        queryset = model.actions.filter(content__contains="OLD_PROD")
        if queryset:
            data = queryset.first().content.split('\n')
            prods = {"old_prod": data[0][9:], "new_prod": data[1][9:]}
        else:
            prods = None
        message = render_to_string('squalaetp/email_format/prod_error_email.html', locals())
        return message


class IhmForm(forms.ModelForm):
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
        super(IhmForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance:
            for field in self.fields:
                self.fields[field].widget.attrs['readonly'] = True
                # self.fields[field].widget.attrs['style'] = 'width: 50%;'


class VinCorvetModalForm(BSModalModelForm):
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

    class Meta:
        model = Xelon
        fields = ['vin']
        widgets = {
            'vin': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': _("Enter the VIN number"), 'autofocus': ''}
            ),
        }

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
        no_fields = ['vin', 'btel', 'radio', 'bsi', 'emf', 'cmm', 'bsm']
        all_data = {key: '' for key in [f.name for f in Corvet._meta.local_fields if f.name not in no_fields]}
        all_data.update({'donnee_date_debut_garantie': None, 'donnee_date_entree_montage': None})
        vin = self.cleaned_data.get("vin")
        if data:
            all_data.update(data)
            if data.get('vin') == vin and data.get('donnee_date_entree_montage'):
                if self.request.is_ajax():
                    xml_corvet_file(self.instance, xml_data, vin)
            if data.get('vin') != vin:
                self.add_error('xml_data', _('XML data does not match VIN'))
        else:
            self.add_error('xml_data', _('Invalid XML data'))
            all_data = data
        return all_data

    def clean(self):
        cleaned_data = super(VinCorvetModalForm, self).clean()
        vin = cleaned_data.get('vin')
        data = cleaned_data.get('xml_data')
        if vin and data and self.request.is_ajax():
            if not data.get('donnee_date_entree_montage'):
                raise forms.ValidationError(_('VIN error !'))
            elif vin != self.instance.vin:
                content = "OLD_VIN: {}\nNEW_VIN: {}".format(self.instance.vin, vin)
                Action.objects.create(content=content, content_object=self.instance)


class ProductModalForm(BSModalModelForm):

    class Meta:
        model = Xelon
        fields = ['modele_produit', 'modele_vehicule']
        widgets = {'modele_vehicule': forms.TextInput(attrs={'readonly': True})}

    def __init__(self, *args, **kwargs):
        xelons = Xelon.objects.exclude(modele_produit="").order_by('modele_produit')
        _data_list = list(xelons.values_list('modele_produit', flat=True).distinct())
        super(ProductModalForm, self).__init__(*args, **kwargs)
        self.fields['modele_produit'].widget = ListTextWidget(data_list=_data_list, name='value-list')

    def clean(self):
        cleaned_data = super(ProductModalForm, self).clean()
        product = cleaned_data.get('modele_produit')
        vehicle = cleaned_data.get('modele_vehicule')
        if product and vehicle and self.request.is_ajax():
            if product != self.instance.modele_produit:
                content = "OLD_PROD: {}\nNEW_PROD: {}".format(self.instance.modele_produit, product)
                Action.objects.create(content=content, content_object=self.instance)
            if vehicle != self.instance.modele_vehicule:
                content = "OLD_VEH: {}\nNEW_VEH: {}".format(self.instance.modele_vehicule, vehicle)
                Action.objects.create(content=content, content_object=self.instance)
