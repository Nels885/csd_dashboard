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
    ref_psa = forms.CharField(label='Réf. PSA', widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=10)
    ref_supplier = forms.CharField(label='Réf. SUP', required=False,
                                   widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=10)

    class Meta:
        model = Repair
        fields = ['ref_psa', 'ref_supplier', 'product_number', 'remark']
        widgets = {
            'product_model': forms.Select(attrs={'class': 'form-control'}),
            'product_number': forms.TextInput(attrs={'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }

    def clean_ref_psa(self):
        data = self.cleaned_data["ref_psa"]
        if not Batch.objects.filter(active=True):
            self.add_error('ref_psa', 'Pas de lot disponible')
        elif not Batch.objects.filter(ecu_model__hw_reference__exact=data):
            self.add_error('ref_psa', 'Pas de lot associé')
        else:
            repair = super(AddRepairForm, self).save(commit=False)
            repair.batch = Batch.objects.filter(
                ecu_model__hw_reference__exact=data, active=True).order_by('end_date').first()
        return data


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
