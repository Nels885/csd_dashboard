import datetime

from django import forms
from django.utils.translation import ugettext as _
from bootstrap_modal_forms.forms import BSModalForm
from tempus_dominus.widgets import DatePicker

from .models import Batch, Repair, SparePart
from utils.conf import DICT_YEAR


class AddBatchFrom(BSModalForm):
    class Meta:
        model = Batch
        fields = ['number', 'quantity', 'start_date', 'end_date']
        widgets = {
            'number': forms.TextInput(attrs={'style': 'width: 40%;', 'maxlength': 3}),
            'quantity': forms.TextInput(attrs={'style': 'width: 40%;', 'maxlength': 3}),
            'start_date': DatePicker(attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            }),
            'end_date': DatePicker(attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True,
            })
        }

    def clean_number(self):
        data = self.cleaned_data['number']
        date = datetime.datetime.now()
        if Batch.objects.filter(year=DICT_YEAR[date.year], number=data):
            self.add_error('number', _('The batch already exists!'))
        return data


class AddRepairForm(BSModalForm):

    class Meta:
        model = Repair
        fields = [
            'batch', 'product_model', 'product_number', 'remark'
        ]
        widgets = {
            'batch': forms.Select(attrs={'class': 'form-control'}),
            'product_model': forms.Select(attrs={'class': 'form-control'}),
            'product_number': forms.TextInput(attrs={'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }


class EditRepairFrom(forms.ModelForm):
    spare_parts = forms.ModelChoiceField(
        queryset=SparePart.objects.all(), required=False, label='Pièces détachées',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    hardware = forms.CharField(
        initial='test', label='HW référence',
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': ''})
    )
    software = forms.CharField(
        label='SW référence',
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': ''})
    )

    class Meta:
        model = Repair
        fields = [
            'identify_number', 'product_number', 'remark', 'quality_control', 'hardware', 'software',
            'checkout',
        ]
        widgets = {
            'identify_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': ''}),
            'product_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': ''}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'readonly': ''}),
            'quality_control': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'checkout': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }


class SparePartForm(forms.Form):
    spare_parts = forms.ModelChoiceField(
        queryset=SparePart.objects.all(), required=False, label='Nom',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    quantity = forms.CharField(label='Quantité', widget=forms.TextInput(attrs={'class': 'form-control'}))


SparePartFormset = forms.formset_factory(SparePartForm, extra=5)
