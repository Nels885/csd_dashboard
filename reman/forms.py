from django.forms import ModelForm, TextInput, Textarea, Select

from .models import Reman


class AddRemanForm(ModelForm):
    class Meta:
        model = Reman
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
