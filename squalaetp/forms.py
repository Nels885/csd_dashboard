from django import forms
from django.utils.translation import ugettext as _
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from bootstrap_modal_forms.forms import BSModalModelForm, BSModalForm
from constance import config

from utils.django.validators import validate_vin, xml_parser
from utils.file.export import xml_corvet_file
from utils.conf import string_to_list
from psa.models import Corvet
from .models import Xelon, Action


class IhmEmailModalForm(BSModalForm):
    to = forms.CharField(label='À', required=True, widget=forms.TextInput())
    cc = forms.CharField(label='Cc', widget=forms.TextInput())
    subject = forms.CharField(label='Objet', required=True, widget=forms.TextInput())
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 10}), required=True)

    def __init__(self, *args, **kwargs):
        super(IhmEmailModalForm, self).__init__(*args, **kwargs)
        self.fields['to'].initial = config.CHANGE_VIN_TO_EMAIL_LIST
        self.fields['cc'].initial = config.VIN_ERROR_TO_EMAIL_LIST

    def send_email(self):
        email = EmailMessage(
            subject=self.cleaned_data['subject'], body=self.cleaned_data['message'],
            to=string_to_list(self.cleaned_data['to']), cc=string_to_list(self.cleaned_data['cc'])
        )
        email.send()

    @staticmethod
    def vin_message(model, request):
        message = "Bonjour,\n\n"
        message += "Vous trouverez ci-dessous, le nouveau VIN pour le dossier {} :\n".format(model.numero_de_dossier)
        try:
            data = model.actions.get(content__contains="OLD_VIN").content.split('\n')
            message += "- Ancien VIN = {}\n".format(data[0][-17:])
            message += "- Nouveau VIN = {}\n".format(data[1][-17:])
        except ObjectDoesNotExist:
            message += "\n### NOUVEAU VIN NON DISPONIBLE ###\n"
        message += "\nCordialement\n\n"
        message += "{} {}".format(request.user.first_name, request.user.last_name)
        return message

    @staticmethod
    def prod_message(model, request):
        message = "Bonjour,\n\n"
        message += f"Vous trouverez ci-dessous, le nouveau modèle produit pour le dossier {model.numero_de_dossier} :\n"
        try:
            data = model.actions.get(content__contains="OLD_PROD").content.split('\n')
            message += f"- Ancien Modèle = {data[0][-17:]}\n"
            message += f"- Nouveau Modèle = {data[1][-17:]}\n"
        except ObjectDoesNotExist:
            message += "\n### NOUVEAU MODELE PRODUIT NON DISPONIBLE ###\n"
        message += "\nCordialement\n\n"
        message += "{} {}".format(request.user.first_name, request.user.last_name)
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


class XelonModalForm(BSModalModelForm):
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
            'vin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _("Enter the VIN number")}),
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
        vin = self.cleaned_data.get("vin")
        if data:
            if data.get('vin') == vin and data.get('donnee_date_entree_montage'):
                if self.request.is_ajax():
                    xml_corvet_file(self.instance, xml_data, vin)
            if data.get('vin') != vin:
                self.add_error('xml_data', _('XML data does not match VIN'))
        else:
            self.add_error('xml_data', _('Invalid XML data'))
        return data

    def clean(self):
        cleaned_data = super(XelonModalForm, self).clean()
        vin = cleaned_data.get('vin')
        data = cleaned_data.get('xml_data')
        if vin and data and self.request.is_ajax():
            if not data.get('donnee_date_entree_montage'):
                raise forms.ValidationError(_('VIN error !'))
            elif vin != self.instance.vin:
                content = "OLD_VIN: {}\nNEW_VIN: {}".format(self.instance.vin, vin)
                Action.objects.create(content=content, content_object=self.instance)
