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
            'batch', 'product_model', 'hardware', 'software', 'remark'
        ]
        widgets = {
            'batch': Select(attrs={'class': 'form-control'}),
            'product_model': Select(attrs={'class': 'form-control'}),
            'hardware': TextInput(attrs={'class': 'form-control'}),
            'software': TextInput(attrs={'class': 'form-control'}),
            'remark': Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }
