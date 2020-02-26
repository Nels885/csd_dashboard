from django.forms import ModelForm, TextInput, Textarea, Select

from bootstrap_modal_forms.forms import BSModalForm

from .models import Batch, Repair


class AddBatchFrom(BSModalForm):
    class Meta:
        model = Batch
        fields = ['number', 'quantity']


class AddRepairForm(ModelForm):
    class Meta:
        model = Repair
        fields = [
            'batch_number', 'identify_number', 'product_model', 'product_reference', 'serial_number', 'remark'
        ]
        widgets = {
            'batch_number': TextInput(attrs={'class': 'form-control'}),
            'identify_number': TextInput(attrs={'class': 'form-control'}),
            'product_model': Select(attrs={'class': 'form-control'}),
            'product_reference': TextInput(attrs={'class': 'form-control'}),
            'serial_number': TextInput(attrs={'class': 'form-control'}),
            'remark': Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }
