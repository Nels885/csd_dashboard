from django import forms
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db.models import Q, Count, Max
from django.contrib.admin.widgets import FilteredSelectMultiple
from bootstrap_modal_forms.forms import BSModalModelForm, BSModalForm
from tempus_dominus.widgets import DatePicker

from constance import config

from .models import Batch, Repair, RepairPart, SparePart, Default, EcuRefBase, EcuType, EcuModel, STATUS_CHOICES
from .tasks import cmd_exportreman_task
from utils.conf import DICT_YEAR
from utils.django.forms.fields import ListTextWidget
from utils.django.validators import validate_identify_number, validate_barcode


"""
~~~~~~~~~~~~~~
MANAGER FORMS
~~~~~~~~~~~~~~
"""

BOX_NUMBER = [(1, 1), (3, 3), (6, 6)]
BATCH_TYPE = [
    ('REMAN_PSA', 'REMAN PSA'), ('ETUDE_PSA', 'ETUDE PSA'), ('REMAN_VOLVO', 'REMAN VOLVO'),
    ('ETUDE_VOLVO', 'ETUDE VOLVO'), ('REPAIR', 'REPAIR')
]


class BatchForm(BSModalModelForm):
    ACTIVE_CHOICES = ((True, _("No")), (False, _("Yes")))
    BARCODE_CHOICES = ((False, _("No")), (True, _("Yes")))

    active = forms.ChoiceField(label="Terminé ?", choices=ACTIVE_CHOICES)
    is_barcode = forms.ChoiceField(label="Nouveau code barre ?", choices=BARCODE_CHOICES)

    class Meta:
        model = Batch
        fields = ['box_quantity', 'active', 'is_barcode', 'start_date', 'end_date']
        widgets = {
            'box_quantity': forms.Select(choices=BOX_NUMBER, attrs={'style': 'width: 40%;'}),
            'start_date': DatePicker(
                attrs={'append': 'fa fa-calendar', 'icon_toggle': True},
                options={'format': 'DD/MM/YYYY'}
            ),
            'end_date': DatePicker(
                attrs={'append': 'fa fa-calendar', 'icon_toggle': True},
                options={'format': 'DD/MM/YYYY'}
            )
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit and not self.request.is_ajax():
            instance.save()
            cmd_exportreman_task.delay('--batch', '--scan_in_out')
        return instance


class AddBatchForm(BSModalModelForm):
    ref_reman = forms.CharField(label="Réf. REMAN", widget=forms.TextInput(), max_length=10)
    type = forms.CharField(label="Type", widget=forms.Select(choices=BATCH_TYPE), )

    class Meta:
        model = Batch
        fields = ['type', 'number', 'quantity', 'box_quantity', 'start_date', 'end_date', 'ref_reman']
        widgets = {
            'number': forms.TextInput(attrs={'style': 'width: 40%;', 'maxlength': 3}),
            'quantity': forms.TextInput(attrs={'style': 'width: 40%;', 'maxlength': 3, 'autofocus': ''}),
            'box_quantity': forms.Select(choices=BOX_NUMBER, attrs={'style': 'width: 40%;'}),
            'start_date': DatePicker(
                attrs={'append': 'fa fa-calendar', 'icon_toggle': True},
                options={'format': 'DD/MM/YYYY'}
            ),
            'end_date': DatePicker(
                attrs={'append': 'fa fa-calendar', 'icon_toggle': True},
                options={'format': 'DD/MM/YYYY'}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            date = timezone.now()
            batchs = Batch.objects.filter(year=DICT_YEAR.get(date.year)).exclude(number__gte=900)
            self.fields["number"].initial = batchs.aggregate(Max('number'))['number__max'] + 1
        except TypeError:
            self.fields['number'].initial = 1

    def clean_number(self):
        data = self.cleaned_data['number']
        batch_type = self.cleaned_data['type']
        date = timezone.now()
        year = DICT_YEAR.get(date.year)
        for key, value in [("REPAIR", "X"), ("VOLVO", "V")]:
            if key in batch_type:
                year = value
        if ("ETUDE" in batch_type and data <= 900) or ("REMAN" in batch_type and data >= 900):
            self.add_error('number', _('Unauthorized batch number!'))
        if Batch.objects.filter(year=year, number=data):
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
                batch = super().save(commit=False)
                batch.ecu_ref_base = ecu
        except EcuRefBase.DoesNotExist:
            self.add_error('ref_reman', 'reference non valide')
        return data

    def save(self, commit=True):
        batch_type = self.cleaned_data['type']
        del self.fields['type']
        batch = super().save(commit=False)
        if commit and not self.request.is_ajax():
            if batch_type == "REPAIR":
                batch.year = "X"
            elif batch_type in ["REMAN_VOLVO", "ETUDE_VOLVO"]:
                batch.year = "V"
                batch.customer = "VOLVO"
                batch.is_barcode = True
            batch.save()
            cmd_exportreman_task.delay('--batch', '--scan_in_out')
        return batch


class RefRemanForm(BSModalModelForm):
    hw_reference = forms.CharField(label="Réf. HW", widget=forms.TextInput(), max_length=20)

    class Meta:
        model = EcuRefBase
        exclude = ['ecu_type']

    def __init__(self, *args, **kwargs):
        ecus = EcuType.objects.exclude(hw_reference="").order_by('hw_reference')
        _data_list = list(ecus.values_list('hw_reference', flat=True).distinct())
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
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
        if commit and not self.request.is_ajax():
            instance.save()
            cmd_exportreman_task.delay('--scan_in_out')
        return instance


class DefaultForm(forms.ModelForm):
    ecu_type = forms.ModelMultipleChoiceField(
        queryset=EcuType.objects.all(), widget=FilteredSelectMultiple("EcuType", is_stacked=False), required=False)

    class Media:
        css = {
            'all': ('/static/admin/css/widgets.css', '/static/admin/css/overrides.css'),
        }
        js = ('/jsi18n/',)

    class Meta:
        model = Default
        fields = '__all__'


"""
~~~~~~~~~~~~~~~~~
TECHNICIAN FORMS
~~~~~~~~~~~~~~~~~
"""


class RepairForm(forms.ModelForm):

    class Meta:
        model = Repair
        fields = "__all__"
        widgets = {
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'readonly': None}),
        }

    def __init__(self, *args, **kwargs):
        super(RepairForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            for field in self.fields:
                self.fields[field].widget.attrs['class'] = "form-control"
                self.fields[field].widget.attrs['readonly'] = True
                self.fields[field].widget.attrs['disabled'] = 'disabled'


class AddRepairForm(BSModalModelForm):
    barcode = forms.CharField(label='Code barre', max_length=50,
                              widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Repair
        fields = ['identify_number', 'barcode', 'remark']
        widgets = {
            'identify_number': forms.TextInput(
                attrs={'class': 'form-control', 'style': 'width: 60%;', 'autofocus': ''}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Batch.objects.all()

    def clean_identify_number(self):
        data = self.cleaned_data["identify_number"]
        self.queryset, message = validate_identify_number(self.queryset, data)
        if message:
            self.add_error('identify_number', message)
        return data

    def clean_barcode(self):
        data = self.cleaned_data["barcode"]
        barcode, batch_type = validate_barcode(data)
        try:
            self.queryset.get(ecu_ref_base__ecu_type__ecumodel__barcode__exact=barcode)
        except (Batch.DoesNotExist, Batch.MultipleObjectsReturned):
            self.add_error('barcode', _('barcode is invalid'))
        return data

    def clean(self):
        cleaned_data = super().clean()
        identify_number = cleaned_data.get("identify_number")
        barcode = cleaned_data.get("barcode")
        if barcode and identify_number:
            if not self.queryset:
                raise forms.ValidationError("Pas de lot associé")
            elif not self.queryset.first().active:
                raise forms.ValidationError("Ce lot n'est plus actif")

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit and not self.request.is_ajax():
            instance.save()
            cmd_exportreman_task.delay('--repair')
        return instance


class SelectRepairForm(BSModalForm):
    repair = forms.CharField(
        label="N° d'identification", max_length=10, required=True,
        widget=forms.TextInput(attrs={'onkeypress': 'return event.keyCode != 13;', 'autofocus': ''})
    )

    class Meta:
        fields = ["repair"]

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get("repair")
        if data:
            try:
                obj = Repair.objects.get(identify_number__exact=data)
                if not obj.batch.active:
                    raise forms.ValidationError("Ce dossier fait partie d'un lot cloturé")
                if obj.closing_date:
                    raise forms.ValidationError("Ce dossier a été cloturé")
            except Repair.DoesNotExist:
                raise forms.ValidationError("Pas de dossier associé")
            except Repair.MultipleObjectsReturned:
                raise forms.ValidationError("Il y a plusieurs dossiers associés")


class EditRepairForm(forms.ModelForm):
    default = forms.ModelChoiceField(queryset=None, required=True, label="Panne", widget=forms.Select())

    class Meta:
        model = Repair
        fields = [
            'identify_number', 'remark', 'comment', 'default', 'recovery', 'face_plate', 'fan', 'locating_pin',
            'metal_case'
        ]
        widgets = {
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'readonly': None}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.batch.ecu_ref_base:
            hw_reference = self.instance.batch.ecu_ref_base.ecu_type.hw_reference
            self.fields['default'].queryset = Default.objects.filter(ecu_type__hw_reference=hw_reference)
        try:
            ecu_model = EcuModel.objects.get(barcode=self.instance.barcode[:10])
            if ecu_model and ecu_model.fan == "OLD":
                self.fields['fan'].required = True
            if ecu_model and ecu_model.rear_bolt == "CHANGE":
                self.fields['locating_pin'].required = True
        except EcuModel.DoesNotExist:
            pass

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            if instance.recovery:
                instance.checkout = False
                instance.closing_date = None
            instance.save()
        return instance


class RepairPartForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_code'].required = False
        self.fields['quantity'].required = False

    class Meta:
        model = RepairPart
        fields = ['product_code', 'quantity']
        widgets = {
            'product_code': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'})
        }
        labels = {'quantity': "Quantité"}

    def clean(self):
        cleaned_data = super().clean()
        product_code = cleaned_data.get("product_code")
        quantity = cleaned_data.get("quantity")
        if not product_code or not quantity:
            raise forms.ValidationError("Veuillez remplir les 2 champs")


class CloseRepairForm(forms.ModelForm):
    new_barcode = forms.CharField(label='Nouveau code barre', max_length=100, required=True, widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        selected_choices = ["En cours"]
        self.fields['status'].choices = [(k, v) for k, v in STATUS_CHOICES if k not in selected_choices]
        instance = getattr(self, 'instance', None)
        if instance and instance.checkout:
            self.fields['status'].widget.attrs['disabled'] = 'disabled'
            self.fields['quality_control'].widget.attrs['disabled'] = 'disabled'
        if instance and not instance.batch.is_barcode:
            self.fields['new_barcode'].required = False

    class Meta:
        model = Repair
        fields = ['identify_number', 'remark', 'new_barcode', 'status', 'quality_control']
        widgets = {
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'readonly': None}),
        }

    def clean_new_barcode(self):
        data = self.cleaned_data["new_barcode"]
        if "#" in data or data == self.instance.barcode:
            self.add_error('new_barcode', _('barcode is invalid'))
        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


"""
~~~~~~~~~~~~~~~
IN / OUT FORMS
~~~~~~~~~~~~~~~
"""


class SelectBatchForm(forms.Form):
    batch = forms.CharField(
        label="Numéro de lot", max_length=10, required=True,
        widget=forms.TextInput(attrs={'onkeypress': 'return event.keyCode != 13;', 'autofocus': ''})
    )

    class Meta:
        fields = ["batch"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        repaired = Count('repairs', filter=Q(repairs__status="Réparé"))
        packed = Count('repairs', filter=Q(repairs__checkout=True))
        self.batch = Batch.objects.all().annotate(repaired=repaired, packed=packed)


class CheckOutSelectBatchForm(SelectBatchForm, BSModalForm):

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get("batch")
        if data:
            try:
                batch = self.batch.get(batch_number__startswith=data)
                if not config.CHECKOUT_BATCH_FILTER_DISABLE:
                    if batch.number >= 900:
                        raise forms.ValidationError("Erreur, il s'agit d'un lot d'Etude")
                    elif batch.year == "X":
                        raise forms.ValidationError("Erreur, il s'agit d'un lot pour le stock")
                    # elif batch.repaired != batch.quantity:
                    #     raise forms.ValidationError(
                    #         "Le lot n'est pas finalisé, {} produit sur {} !".format(batch.repaired, batch.quantity)
                    #     )
            except Batch.DoesNotExist:
                raise forms.ValidationError("Pas de lot associé")
            except Batch.MultipleObjectsReturned:
                raise forms.ValidationError("Il y a plusieurs lots associés")


class CheckOutRepairForm(forms.Form):
    barcode = forms.CharField(
        label="Code barre / QR code", max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control mb-2 mr-sm-4', 'autofocus': ''})
    )

    def __init__(self, *args, **kwargs):
        try:
            batch = Batch.objects.get(batch_number=kwargs.pop("batch_number", None))
        except Batch.DoesNotExist:
            batch = None
        self.repairs = Repair.objects.filter(checkout=False, batch=batch)
        super().__init__(*args, **kwargs)

    def clean_barcode(self):
        data = self.cleaned_data["barcode"]
        try:
            self.repairs = self.repairs.get(Q(identify_number=data[:-1]) | Q(new_barcode=data))
            if not self.repairs.quality_control:
                self.add_error('barcode', "Contrôle qualité non validé, voir avec Atelier.")
        except Repair.DoesNotExist:
            self.add_error('barcode', "Code barre ou QR code invalide")
        return data

    def save(self, commit=True):
        repair = self.repairs
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


class StockSelectBatchForm(SelectBatchForm, BSModalForm):

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get("batch")
        if data:
            try:
                batch = self.batch.get(batch_number__startswith=data)
                if batch.number >= 900:
                    raise forms.ValidationError("Erreur, il s'agit d'un lot d'Etude")
                elif batch.year != "X":
                    raise forms.ValidationError("Erreur, il s'agit d'un lot pour le IN/OUT")
                # elif batch.repaired != batch.quantity:
                #     raise forms.ValidationError(
                #         "Le lot n'est pas finalisé, {} produit sur {} !".format(batch.repaired, batch.quantity)
                #     )
            except Batch.DoesNotExist:
                raise forms.ValidationError("Pas de lot associé")
            except Batch.MultipleObjectsReturned:
                raise forms.ValidationError("Il y a plusieurs lots associés")


class SparePartForm(forms.Form):
    spare_parts = forms.ModelChoiceField(
        queryset=SparePart.objects.filter(code_zone="REMAN PSA").order_by('code_produit'), required=False, label='Nom',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    quantity = forms.CharField(label='Quantité', widget=forms.TextInput(attrs={'class': 'form-control'}))


SparePartFormset = forms.formset_factory(SparePartForm, extra=5)


class CheckPartForm(forms.Form):
    barcode = forms.CharField(label="Code Barre", max_length=100,
                              widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': ''}))

    def clean_barcode(self):
        data = self.cleaned_data['barcode']
        data, message = validate_barcode(data)
        if not message:
            raise forms.ValidationError(
                _("The barcode is invalid"),
                code='invalid',
                params={'value': message},
            )
        return data


class EcuModelForm(forms.ModelForm):
    hw_reference = forms.CharField(label="HW référence", max_length=20, required=True)

    class Meta:
        model = EcuModel
        exclude = ['ecu_type']


class EcuTypeForm(BSModalModelForm):
    class Meta:
        model = EcuType
        exclude = ['spare_part']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['hw_reference'].widget.attrs['readonly'] = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit and not self.request.is_ajax():
            instance.save()
            cmd_exportreman_task.delay('--scan_in_out')
        return instance


class EcuDumpModelForm(BSModalModelForm):
    class Meta:
        model = EcuModel
        fields = ['barcode', 'to_dump']
        widgets = {
            'barcode': forms.TextInput(attrs={"readonly": ""})
        }


class PartEcuModelForm(forms.ModelForm):
    hw_reference = forms.CharField(label="HW référence *", max_length=20, required=True)
    technical_data = forms.CharField(label="Modèle produit *", max_length=50, required=True)
    supplier_oe = forms.CharField(label="Fabriquant *", max_length=50, required=True)

    class Meta:
        model = EcuModel
        fields = ['barcode', 'hw_reference', 'technical_data', 'supplier_oe']
        widgets = {
            'barcode': forms.TextInput(attrs={'readonly': None})
        }
        labels = {
            'barcode': 'Code barre *'
        }

    def __init__(self, *args, **kwargs):
        ecus = EcuType.objects.exclude(hw_reference="").order_by('hw_reference')
        _data_list = list(ecus.values_list('hw_reference', flat=True).distinct())
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance and instance.pk:
            self.fields['hw_reference'].initial = instance.ecu_type.hw_reference
        self.fields['hw_reference'].widget = ListTextWidget(data_list=_data_list, name='value-list')

    def save(self, commit=True):
        instance = super().save(commit=False)
        defaults = {
            "technical_data": self.cleaned_data["technical_data"], "supplier_oe": self.cleaned_data["supplier_oe"]
        }
        obj, created = EcuType.objects.get_or_create(hw_reference=self.cleaned_data["hw_reference"], defaults=defaults)
        instance.ecu_type = obj
        if commit:
            instance.save()
            cmd_exportreman_task.delay('--scan_in_out')
        return instance


class PartEcuTypeForm(forms.ModelForm):
    class Meta:
        model = EcuType
        fields = ['hw_reference', 'technical_data', 'supplier_oe']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hw_reference'].widget.attrs['readonly'] = True


class PartSparePartForm(forms.ModelForm):
    class Meta:
        model = SparePart
        fields = ['code_produit', 'code_emplacement']
