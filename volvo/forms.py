from django import forms
from django.db.models import Q
from bootstrap_modal_forms.forms import BSModalModelForm

from utils.django.forms.fields import ListTextWidget
from utils.django import is_ajax

from reman.models import EcuRefBase, EcuType
from reman.forms import RefRemanForm


class RemanForm(RefRemanForm):
    hw_reference = forms.CharField(label="ASM", widget=forms.TextInput(), max_length=20)
    brand = forms.CharField(label="Brand", widget=forms.TextInput(), max_length=10)

    class Meta:
        model = EcuRefBase
        fields = ['reman_reference', 'hw_reference', 'brand', 'map_data', 'pf_code', 'product_part']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ecus = EcuType.objects.exclude(Q(hw_reference="") | Q(hw_type="ECU")).order_by('hw_reference')
        _hw_list = list(self.ecus.values_list('hw_reference', flat=True).distinct())
        ecu_ref_base = EcuRefBase.objects.exclude(brand="").order_by('brand')
        _brand_list = list(ecu_ref_base.values_list('brand', flat=True).distinct())
        self.fields['hw_reference'].widget = ListTextWidget(data_list=_hw_list, name='hw-list')
        self.fields['brand'].widget = ListTextWidget(data_list=_brand_list, name='brand-list')

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
