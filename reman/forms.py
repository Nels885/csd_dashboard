from django import forms
from django.utils import timezone
from django.utils.translation import ugettext as _
from bootstrap_modal_forms.forms import BSModalForm
from tempus_dominus.widgets import DatePicker

from .models import Batch, Repair, SparePart, Default, EcuRefBase, EcuType, EcuModel
from utils.conf import DICT_YEAR
from utils.django.validators import validate_psa_barcode


class AddBatchForm(BSModalForm):
    ref_reman = forms.CharField(label="Réf. REMAN", widget=forms.TextInput(), max_length=10)

    class Meta:
        model = Batch
        fields = ['number', 'quantity', 'start_date', 'end_date', 'ref_reman']
        widgets = {
            'number': forms.TextInput(attrs={'style': 'width: 40%;', 'maxlength': 3}),
            'quantity': forms.TextInput(attrs={'style': 'width: 40%;', 'maxlength': 3}),
            'start_date': DatePicker(
                attrs={'append': 'fa fa-calendar', 'icon_toggle': True},
                options={'format': 'DD/MM/YYYY'}
            ),
            'end_date': DatePicker(
                attrs={'append': 'fa fa-calendar', 'icon_toggle': True},
                options={'format': 'DD/MM/YYYY'}
            )
        }

    def clean_number(self):
        data = self.cleaned_data['number']
        date = timezone.now()
        if Batch.objects.filter(year=DICT_YEAR[date.year], number=data):
            self.add_error('number', _('The batch already exists!'))
        return data

    def clean_end_date(self):
        end_date = self.cleaned_data['end_date']
        start_date = self.cleaned_data['start_date']
        if end_date < start_date:
            self.add_error('end_date', _('Date is not valid'))
        return end_date

    def clean_ref_reman(self):
        data = self.cleaned_data['ref_reman']
        try:
            ecu = EcuRefBase.objects.get(reman_reference__exact=data)
            if not self.errors:
                batch = super(AddBatchForm, self).save(commit=False)
                batch.ecu_ref_base = ecu
        except EcuRefBase.DoesNotExist:
            self.add_error('ref_reman', 'reference non valide')
        return data


class AddRepairForm(BSModalForm):
    psa_barcode = forms.CharField(label='Code barre PSA', max_length=10,
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}))
    ref_supplier = forms.CharField(label='Réf. SUP', required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=10)

    class Meta:
        model = Repair
        fields = ['identify_number', 'psa_barcode', 'ref_supplier', 'product_number', 'remark']
        widgets = {
            'identify_number': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'product_model': forms.Select(attrs={'class': 'form-control'}),
            'product_number': forms.TextInput(attrs={'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super(AddRepairForm, self).__init__(*args, **kwargs)
        self.batchNumber = None

    def clean_identify_number(self):
        data = self.cleaned_data["identify_number"]
        self.batchNumber = data[:-3] + "000"
        if len(data) < 10 or data == self.batchNumber:
            self.add_error('identify_number', "Ce numéro n'est pas possible")
        elif Repair.objects.filter(identify_number__exact=data):
            self.add_error('identify_number', 'Ce numéro éxiste')
        elif not Batch.objects.filter(batch_number__exact=self.batchNumber):
            self.add_error('identify_number', 'Pas de lot associé')
        return data

    def clean_psa_barcode(self):
        data = self.cleaned_data["psa_barcode"]
        batch = Batch.objects.filter(batch_number__exact=self.batchNumber,
                                     ecu_ref_base__ecumodel__psa_barcode=data).first()
        if not batch:
            self.add_error('psa_barcode', "Code barre PSA incorrecte")
        return data

    def clean(self):
        cleaned_data = super(AddRepairForm, self).clean()
        ref_psa = cleaned_data.get("ref_psa")
        if ref_psa:
            batch = Batch.objects.filter(batch_number__exact=self.batchNumber, ecu_model__hw_reference=ref_psa).first()
            if not batch:
                raise forms.ValidationError("Pas de lot associé")
            elif not batch.active:
                raise forms.ValidationError("Ce lot n'est plus actif")


class EditRepairForm(forms.ModelForm):
    default = forms.ModelChoiceField(queryset=Default.objects.all(), required=True, label="Panne",
                                     widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(EditRepairForm, self).__init__(*args, **kwargs)
        if self.instance.batch.ecu_ref_base:
            technical_data = self.instance.batch.ecu_ref_base.ecu_type.technical_data
            self.fields['default'].queryset = Default.objects.filter(ecu_type__technical_data=technical_data)

    class Meta:
        model = Repair
        fields = ['identify_number', 'product_number', 'remark', 'default', 'quality_control']
        widgets = {
            'identify_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': ''}),
            'product_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': ''}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'quality_control': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }


class CloseRepairForm(forms.Form):
    identify_number = forms.CharField(label="N° d'identification", max_length=10,
                                      widget=forms.TextInput(attrs={'class': 'form-control mb-2 mr-sm-4'}))

    def clean_identify_number(self):
        data = self.cleaned_data["identify_number"]
        repair = Repair.objects.filter(quality_control=True, checkout=False)
        if not repair.filter(identify_number=data):
            self.add_error('identify_number', "N° d'identification invalide")
        return data

    def save(self, commit=True):
        repair = Repair.objects.get(identify_number=self.cleaned_data["identify_number"])
        repair.closing_date = timezone.now()
        repair.checkout = True
        if commit:
            repair.save()
        return repair


class SparePartForm(forms.Form):
    spare_parts = forms.ModelChoiceField(
        queryset=SparePart.objects.filter(code_zone="REMAN PSA").order_by('code_produit'), required=False, label='Nom',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    quantity = forms.CharField(label='Quantité', widget=forms.TextInput(attrs={'class': 'form-control'}))


SparePartFormset = forms.formset_factory(SparePartForm, extra=5)


class CheckPartForm(forms.Form):
    psa_barcode = forms.CharField(label="Code Barre PSA", max_length=10,
                                  widget=forms.TextInput(attrs={'class': 'form-control mb-2 mr-sm-4', 'autofocus': ''}))

    def clean_psa_barcode(self):
        data = self.cleaned_data['psa_barcode']
        message = validate_psa_barcode(data)
        if message:
            raise forms.ValidationError(
                _(message),
                code='invalid',
                params={'value': data},
            )
        return data


class PartEcuModelForm(forms.ModelForm):
    hw_reference = forms.CharField(label="HW référence", max_length=10, required=True)

    class Meta:
        model = EcuModel
        fields = ['psa_barcode', 'hw_reference', 'oe_raw_reference', 'former_oe_reference']
        widgets = {
            'psa_barcode': forms.TextInput(attrs={'readonly': None})
        }


class DefaultForm(BSModalForm):

    class Meta:
        model = Default
        fields = '__all__'
