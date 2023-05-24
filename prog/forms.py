from django.forms import ModelForm, TextInput, Select, CheckboxInput, Form, CharField
from utils.django.forms.fields import ListTextWidget
from django.utils.translation import gettext as _
from django.core.files.storage import FileSystemStorage
from bootstrap_modal_forms.forms import BSModalModelForm
from crum import get_current_user

from utils.django.validators import validate_xelon
from .models import Raspeedi, UnlockProduct, ToolStatus, AET
from squalaetp.models import Xelon
from prog.models import MbedFirmware


class RaspeediForm(ModelForm):
    class Meta:
        model = Raspeedi
        fields = [
            'ref_boitier', 'produit', 'facade', 'type', 'dab', 'cam', 'dump_peedi',
            'cd_version', 'media', 'carto', 'dump_renesas', 'ref_mm', 'connecteur_ecran',
        ]
        widgets = {
            'ref_boitier': TextInput(attrs={'class': 'form-control', 'maxlength': 10}),
            'produit': Select(attrs={'class': 'form-control'}),
            'facade': TextInput(attrs={
                'class': 'form-control', 'pattern': '[A-Z0-9]+', 'style': 'text-transform: uppercase;'
            }),
            'type': Select(attrs={'class': 'form-control'}),
            'dab': CheckboxInput(attrs={'class': 'form-control'}),
            'cam': CheckboxInput(attrs={'class': 'form-control'}),
            'dump_peedi': TextInput(attrs={'class': 'form-control'}),
            'cd_version': TextInput(attrs={'class': 'form-control'}),
            'media': Select(attrs={'class': 'form-control'}),
            'carto': TextInput(attrs={'class': 'form-control'}),
            'dump_renesas': TextInput(attrs={'class': 'form-control'}),
            'ref_mm': TextInput(attrs={'class': 'form-control'}),
            'connecteur_ecran': Select(attrs={'class': 'form-control'}),
        }


class UnlockForm(Form):
    unlock = CharField(
        label='Numéro de dossier', max_length=10,
        widget=TextInput(attrs={'class': 'form-control mb-2 mr-sm-4', 'autofocus': ''})
    )

    def clean_unlock(self):
        data = self.cleaned_data['unlock']
        message = validate_xelon(data)
        if message:
            self.add_error('unlock', _(message))
        else:
            if UnlockProduct.objects.filter(unlock=Xelon.objects.get(numero_de_dossier=data), active=True):
                self.add_error('unlock', _('This Xelon number is already present for unlocking'))
        return data

    def save(self, commit=True):
        user = get_current_user()
        unlock = self.cleaned_data['unlock']
        instance = UnlockProduct.objects.create(user=user, unlock=Xelon.objects.get(numero_de_dossier=unlock))
        if commit:
            instance.save()
        return instance


class ToolStatusForm(BSModalModelForm):
    class Meta:
        model = ToolStatus
        fields = '__all__'


class AETModalForm(BSModalModelForm):
    class Meta:
        model = AET
        fields = '__all__'


class AETAddSoftwareModalForm(BSModalModelForm):
    class Meta:
        model = MbedFirmware
        fields = ['name', 'version', 'filepath']

    # def save(self, commit=True):
    #     instance = super().save(commit=False)
    #     if self.request.is_ajax():
    #         file = self.request.FILES.get('filepath')
    #         print(file)
    #         instance.filepath = file
    #     if commit and not self.request.is_ajax():
    #         instance.save()
    #         # MbedFirmware.objects.create(name=self.cleaned_data['name'], version=self.cleaned_data['version'],
    #         #                             filepath=request_file)
    #     return instance


class AETSendSoftwareForm(BSModalModelForm):
    select_target = CharField(label='Mbed à mettre à jour', max_length=500, required=False)
    select_firmware = CharField(label='Nom du firmware Mbed', max_length=500, required=False)

    def __init__(self, pk=None, *args, **kwargs):
        if pk is not None:
            aet = AET.objects.get(id=pk)
            _target_list = list(aet.mbed_list.split(";\r\n"))
        else:
            _target_list = None
        firmwares = MbedFirmware.objects.all()
        _firmware_list = list(firmwares.values_list('name', flat=True).distinct())
        super().__init__(*args, **kwargs)
        self.fields['select_target'].widget = ListTextWidget(data_list=_target_list, name='target-list')
        self.fields['select_firmware'].widget = ListTextWidget(data_list=_firmware_list, name='firmware-list')

    class Meta:
        model = MbedFirmware
        fields = '__all__'

