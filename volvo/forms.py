from django import forms
from bootstrap_modal_forms.forms import BSModalModelForm

from utils.django.forms.fields import ListTextWidget

from .models import SemRefBase, SemType


class RemanForm(BSModalModelForm):
    asm_reference = forms.CharField(label="ASM", widget=forms.TextInput(), max_length=20)

    class Meta:
        model = SemRefBase
        exclude = ['ecu_type']

    def __init__(self, *args, **kwargs):
        ecus = SemType.objects.exclude(asm_reference="").order_by('asm_reference')
        _data_list = list(ecus.values_list('asm_reference', flat=True).distinct())
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['reman_reference'].widget.attrs['readonly'] = True
            self.fields['asm_reference'].initial = instance.ecu_type.asm_reference
        self.fields['asm_reference'].widget = ListTextWidget(data_list=_data_list, name='value-list')

    def clean_asm_reference(self):
        data = self.cleaned_data['asm_reference']
        try:
            ecu = SemType.objects.get(asm_reference__exact=data)
            if not self.errors:
                reman = super().save(commit=False)
                reman.ecu_type = ecu
        except SemType.DoesNotExist:
            self.add_error('asm_reference', "réf. HW n'existe pas.")
        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit and not self.request.is_ajax():
            instance.save()
        return instance


class SemTypeForm(BSModalModelForm):
    class Meta:
        model = SemType
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['asm_reference'].widget.attrs['readonly'] = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit and not self.request.is_ajax():
            instance.save()
        return instance
