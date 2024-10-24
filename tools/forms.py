from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
from bootstrap_modal_forms.forms import BSModalModelForm
from crum import get_current_user
from tempus_dominus.widgets import DatePicker

from utils.conf import string_to_list
from utils.django import is_ajax
from utils.django.validators import validate_xelon
from utils.django.forms.fields import ListTextWidget
from utils.django.forms import MultipleFileField

from squalaetp.models import Xelon
from .models import (
    TagXelon, CsdSoftware, ThermalChamber, Suptech, SuptechItem, Message, SuptechFile, ConfigFile, Infotech,
    InfotechMailingList
)
from .tasks import send_email_task


class TagXelonForm(BSModalModelForm):
    class Meta:
        model = TagXelon
        fields = ['xelon', 'calibre', 'telecode', 'comments']
        widgets = {
            'xelon': forms.TextInput(attrs={'onkeypress': 'return event.keyCode != 13;', 'autofocus': ''}),
            'calibre': forms.Select(attrs={'class': 'custom-select'}),
            'telecode': forms.Select(attrs={'class': 'custom-select'}),
            'comments': forms.Textarea()
        }
        labels = {'calibre': 'Calibration fait avec'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comments'].initial = 'RAS OK'

    def clean_xelon(self):
        data = self.cleaned_data['xelon']
        message = validate_xelon(data)
        if message:
            self.add_error('xelon', _(message))
        return data


class SoftwareForm(forms.ModelForm):
    class Meta:
        model = CsdSoftware
        fields = [
            'jig', 'new_version', 'old_version', 'link_download', 'status', 'validation_date'
        ]
        widgets = {
            'jig': forms.TextInput(attrs={'class': 'form-control'}),
            'new_version': forms.TextInput(attrs={'class': 'form-control'}),
            'old_version': forms.TextInput(attrs={'class': 'form-control'}),
            'link_download': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'validation_date': forms.DateInput(attrs={'class': 'form-control'}),
        }


class ThermalFrom(forms.ModelForm):
    class Meta:
        model = ThermalChamber
        fields = ['operating_mode', 'xelon_number']
        widgets = {
            'operating_mode': forms.Select(attrs={'class': 'custom-select form-control'}),
            'xelon_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class SuptechModalForm(BSModalModelForm):
    ITEM_CHOICES = [
        ('', '---------'),
        ('Hot Line Tech', 'Hot Line Tech'), ('Support Admin', 'Support Admin'), ('R.M.', 'R.M.'),
        ('Temps Annexe', 'Temps Annexe'), ('Validation Tech', 'Validation Tech'),
        ('Retour Autotronik', 'Retour Autotronik'), ('Probleme process', 'Probleme process'),
        ('Informatique/Reseau', 'Informatique/Reseau'), ('Inter Maintenance(AF/YM)', 'Inter Maintenance(AF/YM)'),
        ('Scan IN/OUT', 'Scan IN/OUT'), ('Autres... (Avec resumé)', 'Autres... (Avec resumé)')
    ]
    username = forms.CharField(max_length=50, required=True)
    item = forms.ModelChoiceField(queryset=SuptechItem.objects.filter(is_active=True))
    custom_item = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'readonly': ''}), required=False)
    to = forms.CharField(max_length=5000, widget=forms.TextInput(), required=True)
    cc = forms.CharField(max_length=5000, widget=forms.Textarea(attrs={"rows": 2, 'readonly': ''}), required=False)
    attach = MultipleFileField(required=False)

    class Meta:
        model = Suptech
        fields = [
            'username', 'xelon', 'product', 'item', 'custom_item', 'category', 'is_48h', 'time', 'to', 'cc', 'info',
            'rmq', 'attach'
        ]

    def __init__(self, *args, **kwargs):
        users = User.objects.all()
        xelons = Xelon.objects.all()
        _user_list = list(users.values_list('username', flat=True).distinct())
        _prod_list = list(xelons.values_list('modele_produit', flat=True).distinct())
        super().__init__(*args, **kwargs)
        if self.request.user:
            self.fields['username'].initial = self.request.user.username
        self.fields['username'].widget = ListTextWidget(data_list=_user_list, name='user-list')
        self.fields['product'].widget = ListTextWidget(data_list=_prod_list, name='prod-list')

    def clean_username(self):
        data = self.cleaned_data['username']
        try:
            data = User.objects.get(username=data)
        except User.DoesNotExist:
            self.add_error('username', _("Username not found."))
        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        user = self.cleaned_data['username']
        instance.date = timezone.now()
        instance.user = f"{user.first_name} {user.last_name}"
        instance.created_by = user
        instance.created_at = timezone.now()
        if commit and not is_ajax(self.request):
            files = self.request.FILES.getlist('attach')
            for field in ['username', 'custom_item', 'attach']:
                del self.fields[field]
            if self.cleaned_data['custom_item']:
                instance.item = f"{self.cleaned_data['item']} - {self.cleaned_data['custom_item']}"
            instance.save()
            if files:
                [SuptechFile.objects.create(file=f, suptech=instance) for f in files]
        return instance


class SuptechResponseForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('', '---------'), ('En Cours', 'En Cours'), ('Cloturée', 'Cloturée'), ('Annulée', 'Annulée')
    ]
    to = forms.CharField(max_length=5000, widget=forms.Textarea(attrs={'rows': 2, 'readonly': ''}))
    cc = forms.CharField(max_length=5000, widget=forms.Textarea(attrs={'rows': 2, 'readonly': ''}))
    action = forms.CharField(widget=forms.Textarea(), required=True)
    status = forms.CharField(widget=forms.Select(choices=STATUS_CHOICES), required=True)
    deadline = forms.DateField(required=False, input_formats=['%d/%m/%Y'], widget=DatePicker(
        attrs={'append': 'fa fa-calendar', 'icon_toggle': True}, options={'format': 'DD/MM/YYYY'},
    ))
    attach = MultipleFileField(required=False)

    class Meta:
        model = Suptech
        fields = [
            'user', 'xelon', 'item', 'category', 'time', 'is_48h', 'to', 'cc', 'info', 'rmq', 'action', 'status',
            'deadline', 'attach'
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)
        user = get_current_user()
        instance.modified_by = user
        instance.modified_at = timezone.now()
        if commit:
            files = self.cleaned_data['attach']
            del self.fields['attach']
            instance.save()
            if instance.action:
                content = {"type": "action", "msg": instance.action}
                Message.objects.create(
                    content=content, added_at=instance.modified_at, added_by=instance.modified_by,
                    content_object=instance)
            if files:
                [SuptechFile.objects.create(file=f, suptech=instance, is_action=True) for f in files]
            # cmd_suptech_task.delay()
        return instance


class EmailMessageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(), required=True)

    @staticmethod
    def send_email(request, instance):
        try:
            name = instance._meta.verbose_name
            redirect_url = reverse(f'tools:{name.lower()}_detail', args=[instance.id])
            current_site = get_current_site(request)
            subject = f"[{name.upper()}_{instance.id}] {instance.item}"
            to_list = instance.to + "; " + instance.created_by.email
            cc_list = [request.user.email] + string_to_list(instance.cc)
            context = {'url': current_site.domain + redirect_url}
            message = render_to_string('tools/email_format/message_email.html', context)
            send_email_task.delay(
                subject=subject, body=message, from_email=settings.EMAIL_HOST_USER, to=to_list, cc=cc_list
            )
            return True
        except AttributeError:
            return False


class ConfigFileForm(BSModalModelForm):
    file = forms.FileField(
        label="Fichier config", widget=forms.ClearableFileInput(attrs={'multiple': False}), required=False)

    class Meta:
        model = ConfigFile
        fields = ['name', 'path', 'file']

    def save(self, commit=True):
        instance = super().save(commit=False)
        file = self.request.FILES.get('file')
        if commit and file:
            instance.filename = file.name
            instance.content = file.read().decode('utf-8')
            instance.save()
        return instance


class SelectConfigForm(forms.Form):
    select = forms.CharField(label='Selection', max_length=500, required=False)

    def __init__(self, *args, **kwargs):
        configs = ConfigFile.objects.all()
        _data_list = list(configs.values_list('name', flat=True).distinct())
        super().__init__(*args, **kwargs)
        self.fields['select'].widget = ListTextWidget(data_list=_data_list, name='value-list')

    def clean_select(self):
        data = self.cleaned_data['select']
        try:
            obj = ConfigFile.objects.get(name=data)
            data = obj.pk
        except ConfigFile.DoesNotExist:
            data = -1
        return data


class EditConfigForm(forms.ModelForm):

    class Meta:
        model = ConfigFile
        fields = ['content']


class InfotechModalForm(BSModalModelForm):
    username = forms.CharField(max_length=50, required=True)
    item = forms.CharField(max_length=200, required=True)
    mailing = forms.ModelChoiceField(queryset=InfotechMailingList.objects.filter(is_active=True))
    to = forms.CharField(max_length=5000, widget=forms.Textarea(attrs={"rows": 2, 'readonly': ''}), required=False)
    cc = forms.CharField(max_length=5000, widget=forms.Textarea(attrs={"rows": 2, 'readonly': ''}), required=False)
    info = forms.CharField(max_length=5000, widget=forms.Textarea(), required=True)

    def __init__(self, *args, **kwargs):
        users = User.objects.all()
        _user_list = list(users.values_list('username', flat=True).distinct())
        super().__init__(*args, **kwargs)
        if self.request.user:
            self.fields['username'].initial = self.request.user.username
        self.fields['username'].widget = ListTextWidget(data_list=_user_list, name='user-list')

    class Meta:
        model = Infotech
        fields = ['username', 'item', 'mailing', 'to', 'cc', 'info']

    def clean_username(self):
        data = self.cleaned_data['username']
        try:
            data = User.objects.get(username=data)
        except User.DoesNotExist:
            self.add_error('username', _("Username not found."))
        return data

    def send_email(self):
        current_site = get_current_site(self.request)
        from_email = self.cleaned_data["username"].email
        subject = f"[INFOTECH_{self.instance.id}] {self.instance.item}"
        context = {'email': from_email, 'instance': self.instance, 'domain': current_site.domain}
        message = render_to_string('tools/email_format/infotech_email.html', context)
        send_email_task.delay(
            subject=subject, body=message, from_email=from_email, to=string_to_list(self.instance.to),
            cc=([from_email] + string_to_list(self.instance.cc))
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.created_by = self.cleaned_data['username']
        if commit and not is_ajax(self.request):
            for field in ['username', 'mailing']:
                del self.fields[field]
            instance.save()
            self.send_email()
        return instance


class InfotechActionForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('', '---------'), ('En Cours', 'En Cours'), ('Cloturée', 'Cloturée')
    ]
    action = forms.CharField(widget=forms.Textarea(), required=True)
    status = forms.CharField(widget=forms.Select(choices=STATUS_CHOICES), required=True)

    class Meta:
        model = Infotech
        fields = ['item', 'info', 'action', 'status']

    def send_email(self, request):
        try:
            current_site = get_current_site(request)
            subject = f"[INFOTECH_{self.instance.id}] {self.instance.item}"
            context = {'user': request.user, 'obj': self.instance, 'domain': current_site.domain}
            message = render_to_string('tools/email_format/infotech_action_email.html', context)
            cc_list = [request.user.email] + string_to_list(self.instance.cc)
            send_email_task.delay(
                subject=subject, body=message, from_email=request.user.email, to=self.instance.to,
                cc=cc_list
            )
            return True
        except AttributeError:
            return False

    def save(self, commit=True):
        instance = super().save(commit=False)
        user = get_current_user()
        instance.modified_by = user
        instance.modified_at = timezone.now()
        if commit:
            instance.save()
            if instance.action:
                content = {"type": "action", "msg": instance.action}
                Message.objects.create(
                    content=content, added_at=instance.modified_at, added_by=instance.modified_by,
                    content_object=instance)
        return instance
