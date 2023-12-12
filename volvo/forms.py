from django import forms
from bootstrap_modal_forms.forms import BSModalModelForm

from utils.django.forms.fields import ListTextWidget
from utils.django import is_ajax

from reman.models import EcuRefBase, EcuType


class RemanForm(BSModalModelForm):
    hw_reference = forms.CharField(label="ASM", widget=forms.TextInput(), max_length=20)

    class Meta:
        model = EcuRefBase
        fields = ['reman_reference', 'hw_reference', 'brand', 'map_data', 'pf_code', 'product_part']

    def __init__(self, *args, **kwargs):
        ecus = EcuType.objects.exclude(hw_reference="").order_by('hw_reference')
        _data_list = list(ecus.values_list('hw_reference', flat=True).distinct())
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['reman_reference'].widget.attrs['readonly'] = True
            self.fields['hw_reference'].initial = instance.ecu_type.hw_reference
        self.fields['hw_reference'].widget = ListTextWidget(data_list=_data_list, name='value-list')

    def clean_hw_reference(self):
        data = self.cleaned_data['hw_reference']
        try:
            ecu = EcuType.objects.get(hw_reference__exact=data)
            if not self.errors:
                reman = super().save(commit=False)
                reman.ecu_type = ecu
        except EcuType.DoesNotExist:
            self.add_error('hw_reference', "réf. HW n'existe pas.")
        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit and not is_ajax(self.request):
            instance.save()
        return instance


class SemTypeForm(BSModalModelForm):
    class Meta:
        model = EcuType
        exclude = ["spare_part"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['hw_reference'].widget.attrs['readonly'] = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit and not is_ajax(self.request):
            instance.save()
        return instance
