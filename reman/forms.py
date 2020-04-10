import datetime

from django import forms
from django.utils.translation import ugettext as _
from bootstrap_modal_forms.forms import BSModalForm
from tempus_dominus.widgets import DatePicker

from .models import Batch, Repair, SparePart, EcuModel
from utils.conf import DICT_YEAR


class AddBatchFrom(BSModalForm):
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
            ),
            'ecu_model': forms.Select(),
        }

    def clean_number(self):
        data = self.cleaned_data['number']
        date = datetime.datetime.now()
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
        if not EcuModel.objects.filter(es_reference__exact=data):
            self.add_error('ref_reman', 'reference non valide')
        else:
            batch = super(AddBatchFrom, self).save(commit=False)
            batch.ecu_model = EcuModel.objects.filter(es_reference__exact=data).first()
        return data


class AddRepairForm(BSModalForm):
    ref_psa = forms.CharField(label='Réf. PSA', max_length=10,
                              widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}))
    ref_supplier = forms.CharField(label='Réf. SUP', required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=10)

    class Meta:
        model = Repair
        fields = ['identify_number', 'ref_psa', 'ref_supplier', 'product_number', 'remark']
        widgets = {
            'identify_number': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'product_model': forms.Select(attrs={'class': 'form-control'}),
            'product_number': forms.TextInput(attrs={'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def clean_ref_psa(self):
        data = self.cleaned_data["ref_psa"]
        batch = Batch.objects.filter(batch_number__exact=self.batchNumber, ecu_model__hw_reference=data).first()
        if not batch:
            self.add_error('ref_psa', "Référence incorrecte")
        return data

    def clean(self):
        cleaned_data = super().clean()
        ref_psa = cleaned_data.get("ref_psa")
        if ref_psa:
            batch = Batch.objects.filter(batch_number__exact=self.batchNumber, ecu_model__hw_reference=ref_psa).first()
            if not batch:
                raise forms.ValidationError("Pas de lot associé")
            elif not batch.active:
                raise forms.ValidationError("Ce lot n'est plus actif")


class EditRepairFrom(forms.ModelForm):
    class Meta:
        model = Repair
        fields = ['identify_number', 'product_number', 'remark', 'quality_control']
        widgets = {
            'identify_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': ''}),
            'product_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': ''}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'readonly': ''}),
            'quality_control': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }


class SparePartForm(forms.Form):
    spare_parts = forms.ModelChoiceField(
        queryset=SparePart.objects.all(), required=False, label='Nom',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    quantity = forms.CharField(label='Quantité', widget=forms.TextInput(attrs={'class': 'form-control'}))


SparePartFormset = forms.formset_factory(SparePartForm, extra=5)
