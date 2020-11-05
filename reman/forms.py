from django import forms
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models import Q, Count
from bootstrap_modal_forms.forms import BSModalModelForm, BSModalForm
from tempus_dominus.widgets import DatePicker

from .models import Batch, Repair, SparePart, Default, EcuRefBase, EcuType, EcuModel, STATUS_CHOICES
from utils.conf import DICT_YEAR
from utils.django.validators import validate_psa_barcode


"""
~~~~~~~~~~~~~~
MANAGER FORMS
~~~~~~~~~~~~~~
"""


class AddBatchForm(BSModalModelForm):
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


class DefaultForm(BSModalModelForm):
    class Meta:
        model = Default
        fields = '__all__'


"""
~~~~~~~~~~~~~~~~~
TECHNICIAN FORMS
~~~~~~~~~~~~~~~~~
"""


class AddRepairForm(BSModalModelForm):
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
        self.queryset = Batch.objects.all()

    def clean_identify_number(self):
        data = self.cleaned_data["identify_number"]
        batch_number = data[:-3] + "000"
        self.queryset = self.queryset.filter(batch_number__exact=batch_number)
        if self.queryset and self.queryset.filter(repairs__identify_number=data):
            self.add_error("identify_number", "Ce numéro éxiste")
        elif data[-3:] == "000":
            self.add_error("identify_number", "Ce numéro n'est pas autorisé")
        return data

    def clean_psa_barcode(self):
        data = self.cleaned_data["psa_barcode"]
        queryset = self.queryset.filter(ecu_ref_base__ecu_type__ecumodel__psa_barcode=data)
        if not queryset:
            self.add_error('psa_barcode', "Code barre PSA incorrecte")
        return data

    def clean(self):
        cleaned_data = super(AddRepairForm, self).clean()
        identify_number = cleaned_data.get("identify_number")
        psa_barcode = cleaned_data.get("psa_barcode")
        if psa_barcode and identify_number:
            if not self.queryset:
                raise forms.ValidationError("Pas de lot associé")
            elif not self.queryset.first().active:
                raise forms.ValidationError("Ce lot n'est plus actif")


class EditRepairForm(forms.ModelForm):
    default = forms.ModelChoiceField(queryset=Default.objects.all(), required=True, label="Panne",
                                     widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(EditRepairForm, self).__init__(*args, **kwargs)
        if self.instance.batch.ecu_ref_base:
            hw_reference = self.instance.batch.ecu_ref_base.ecu_type.hw_reference
            self.fields['default'].queryset = Default.objects.filter(ecu_type__hw_reference=hw_reference)

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


"""
~~~~~~~~~~~~~~~
IN / OUT FORMS
~~~~~~~~~~~~~~~
"""


class CheckOutSelectBatchForm(BSModalForm):
    batch = forms.CharField(
        label="Numéro de lot", max_length=10, required=True,
        widget=forms.TextInput(attrs={'onkeypress': 'return event.keyCode != 13;', 'autofocus': ''})
    )

    class Meta:
        fields = ["batch"]

    def __init__(self, *args, **kwargs):
        super(CheckOutSelectBatchForm, self).__init__(*args, **kwargs)
        repaired = Count('repairs', filter=Q(repairs__status="Réparé"))
        packed = Count('repairs', filter=Q(repairs__checkout=True))
        self.batch = Batch.objects.all().annotate(repaired=repaired, packed=packed)

    def clean_batch(self):
        data = self.cleaned_data["batch"]
        batchs = self.batch.filter(batch_number=data)
        if not batchs:
            self.add_error("batch", "Pas de lot associé")
        elif len(batchs) > 1:
            self.add_error("batch", "Il y a plusieurs lots associés")
        else:
            batch = batchs.first()
            if batch.repaired != batch.quantity:
                self.add_error(
                    "batch", "Le lot n'est pas finalisé, {} produit sur {} !".format(batch.repaired, batch.quantity)
                )
        return data


class CheckOutRepairForm(forms.Form):
    identify_number = forms.CharField(
        label="N° d'identification", max_length=11,
        widget=forms.TextInput(attrs={'class': 'form-control mb-2 mr-sm-4', 'autofocus': ''})
    )

    def __init__(self, *args, **kwargs):
        batch_number = kwargs.pop("batch_number", None)
        super(CheckOutRepairForm, self).__init__(*args, **kwargs)
        if batch_number:
            batch = Batch.objects.filter(batch_number=batch_number).first()
        else:
            batch = None
        self.repairs = Repair.objects.filter(quality_control=True, checkout=False, batch=batch)

    def clean_identify_number(self):
        data = self.cleaned_data["identify_number"]
        if data[-1] != "R" or not self.repairs.filter(identify_number=data[:-1]):
            self.add_error('identify_number', "N° d'identification invalide")
        return data

    def save(self, commit=True):
        repair = self.repairs.get(identify_number=self.cleaned_data["identify_number"][:-1])
        repair.closing_date = timezone.now()
        repair.checkout = True
        if commit:
            repair.save()
        return repair


"""
~~~~~~~~~~~~~~~~~~
SPARE PARTS FORMS
~~~~~~~~~~~~~~~~~~
"""


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
