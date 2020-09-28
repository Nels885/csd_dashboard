from django import forms
from django.utils import timezone
from django.utils.translation import ugettext as _
from bootstrap_modal_forms.forms import BSModalForm
from tempus_dominus.widgets import DatePicker

from .models import Batch, Repair, SparePart, Default, EcuRefBase, EcuType, EcuModel, STATUS_CHOICES
from utils.conf import DICT_YEAR
from utils.django.validators import validate_psa_barcode


class AddBatchForm(BSModalForm):
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
            )
        }

    def clean_number(self):
        data = self.cleaned_data['number']
        date = timezone.now()
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
        try:
            ecu = EcuRefBase.objects.get(reman_reference__exact=data)
            if not self.errors:
                batch = super(AddBatchForm, self).save(commit=False)
                batch.ecu_ref_base = ecu
        except EcuRefBase.DoesNotExist:
            self.add_error('ref_reman', 'reference non valide')
        return data


class AddRepairForm(BSModalForm):
    psa_barcode = forms.CharField(label='Code barre PSA', max_length=10,
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}))

    class Meta:
        model = Repair
        fields = ['identify_number', 'psa_barcode', 'remark']
        widgets = {
            'identify_number': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 50%;'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super(AddRepairForm, self).__init__(*args, **kwargs)
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

    def clean_psa_barcode(self):
        data = self.cleaned_data["psa_barcode"]
        batch = Batch.objects.filter(batch_number__exact=self.batchNumber,
                                     ecu_ref_base__ecu_type__ecumodel__psa_barcode=data).first()
        if not batch:
            self.add_error('psa_barcode', "Code barre PSA incorrecte")
        return data

    def clean(self):
        cleaned_data = super(AddRepairForm, self).clean()
        psa_barcode = cleaned_data.get("psa_barcode")
        if psa_barcode:
            batch = Batch.objects.filter(batch_number__exact=self.batchNumber,
                                         ecu_ref_base__ecu_type__ecumodel__psa_barcode=psa_barcode).first()
            if not batch:
                raise forms.ValidationError("Pas de lot associé")
            elif not batch.active:
                raise forms.ValidationError("Ce lot n'est plus actif")


class EditRepairForm(forms.ModelForm):
    default = forms.ModelChoiceField(queryset=Default.objects.all(), required=True, label="Panne",
                                     widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(EditRepairForm, self).__init__(*args, **kwargs)
        if self.instance.batch.ecu_ref_base:
            technical_data = self.instance.batch.ecu_ref_base.ecu_type.technical_data
            self.fields['default'].queryset = Default.objects.filter(ecu_type__technical_data=technical_data)

    class Meta:
        model = Repair
        fields = ['identify_number', 'product_number', 'remark', 'comment', 'default']
        widgets = {
            'identify_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': None}),
            'product_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': None}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'readonly': None}),
        }


class CloseRepairForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CloseRepairForm, self).__init__(*args, **kwargs)
        selected_choices = ["En cours"]
        self.fields['status'].choices = [(k, v) for k, v in STATUS_CHOICES if k not in selected_choices]
        instance = getattr(self, 'instance', None)
        if instance and instance.checkout:
            self.fields['status'].widget.attrs['disabled'] = 'disabled'
            self.fields['quality_control'].widget.attrs['disabled'] = 'disabled'

    class Meta:
        model = Repair
        fields = ['identify_number', 'product_number', 'remark', 'status', 'quality_control']
        widgets = {
            'identify_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': None}),
            'product_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': None}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'readonly': None}),
            'status': forms.Select(attrs={'class': 'form-control custom-select '}),
            'quality_control': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        instance = super(CloseRepairForm, self).save(commit=False)
        if commit:
            if instance.status != "Réparé":
                instance.quality_control = False
            instance.save()
        return instance


class CheckOutRepairForm(forms.Form):
    identify_number = forms.CharField(
        label="N° d'identification", max_length=11,
        widget=forms.TextInput(attrs={'class': 'form-control mb-2 mr-sm-4', 'autofocus': ''})
    )

    def clean_identify_number(self):
        data = self.cleaned_data["identify_number"]
        repair = Repair.objects.filter(quality_control=True, checkout=False)
        if data[-1] != "R" or not repair.filter(identify_number=data[:-1]):
            self.add_error('identify_number', "N° d'identification invalide")
        return data

    def save(self, commit=True):
        repair = Repair.objects.get(identify_number=self.cleaned_data["identify_number"][:-1])
        repair.closing_date = timezone.now()
        repair.checkout = True
        if commit:
            repair.save()
        return repair


class SparePartForm(forms.Form):
    spare_parts = forms.ModelChoiceField(
        queryset=SparePart.objects.filter(code_zone="REMAN PSA").order_by('code_produit'), required=False, label='Nom',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    quantity = forms.CharField(label='Quantité', widget=forms.TextInput(attrs={'class': 'form-control'}))


SparePartFormset = forms.formset_factory(SparePartForm, extra=5)


class CheckPartForm(forms.Form):
    psa_barcode = forms.CharField(label="Code Barre PSA", max_length=10,
                                  widget=forms.TextInput(attrs={'class': 'form-control mb-2 mr-sm-4', 'autofocus': ''}))

    def clean_psa_barcode(self):
        data = self.cleaned_data['psa_barcode']
        message = validate_psa_barcode(data)
        if message:
            raise forms.ValidationError(
                _(message),
                code='invalid',
                params={'value': data},
            )
        return data


class EcuModelForm(forms.ModelForm):
    hw_reference = forms.CharField(label="HW référence", max_length=10, required=True)

    class Meta:
        model = EcuModel
        exclude = ['ecu_type']


class PartEcuModelForm(forms.ModelForm):
    hw_reference = forms.CharField(label="HW référence *", max_length=10, required=True)

    class Meta:
        model = EcuModel
        fields = ['psa_barcode', 'hw_reference', 'oe_raw_reference', 'former_oe_reference']
        widgets = {
            'psa_barcode': forms.TextInput(attrs={'readonly': None})
        }
        labels = {
            'psa_barcode': 'Code barre PSA *'
        }

    def save(self, commit=True):
        instance = super(PartEcuModelForm, self).save(commit=False)
        type_obj, type_created = EcuType.objects.update_or_create(hw_reference=self.cleaned_data["hw_reference"])
        instance.ecu_type = type_obj
        if commit:
            instance.save()
        return instance


class PartEcuTypeForm(forms.ModelForm):
    class Meta:
        model = EcuType
        fields = ['hw_reference', 'technical_data', 'supplier_oe']

    def __init__(self, *args, **kwargs):
        super(PartEcuTypeForm, self).__init__(*args, **kwargs)
        # instance = getattr(self, 'instance', None)
        # if instance and instance.technical_data:
        #     self.fields['technical_data'].widget.attrs['readonly'] = True
        # if instance and instance.supplier_oe:
        #     self.fields['supplier_oe'].widget.attrs['readonly'] = True
        self.fields['hw_reference'].widget.attrs['readonly'] = True


class PartSparePartForm(forms.ModelForm):
    class Meta:
        model = SparePart
        fields = ['code_produit', 'code_emplacement']

    def __init__(self, *args, **kwargs):
        super(PartSparePartForm, self).__init__(*args, **kwargs)
        # instance = getattr(self, 'instance', None)
        # if instance and instance.code_emplacement:
        #     for field in self.fields:
        #         self.fields[field].widget.attrs['readonly'] = True
        # else:
        self.fields['code_produit'].widget.attrs['readonly'] = True
        # self.fields['code_emplacement'].required = True


class DefaultForm(BSModalForm):
    class Meta:
        model = Default
        fields = '__all__'
