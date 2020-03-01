import datetime

from django import forms
from django.utils.translation import ugettext as _
from bootstrap_modal_forms.forms import BSModalForm
from tempus_dominus.widgets import DatePicker

from .models import Batch, Repair
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


class AddRepairForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = [
            'batch', 'product_model', 'hardware', 'software', 'remark'
        ]
        widgets = {
            'batch': forms.Select(attrs={'class': 'form-control'}),
            'product_model': forms.Select(attrs={'class': 'form-control'}),
            'hardware': forms.TextInput(attrs={'class': 'form-control'}),
            'software': forms.TextInput(attrs={'class': 'form-control'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }
