from django import forms
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.core.mail import EmailMessage
from django.core.management import call_command
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from bootstrap_modal_forms.forms import BSModalModelForm
from crum import get_current_user
from constance import config

from utils.conf import string_to_list
from utils.django.validators import validate_xelon
from utils.django.forms.fields import ListTextWidget

from .models import TagXelon, CsdSoftware, ThermalChamber, Suptech


class TagXelonForm(BSModalModelForm):
    class Meta:
        model = TagXelon
        fields = ['xelon', 'comments']
        widgets = {
            'xelon': forms.TextInput(
                attrs={'class': 'form-control col-sm-6', 'onkeypress': 'return event.keyCode != 13;', 'autofocus': ''}
            ),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        }

    def __init__(self, *args, **kwargs):
        super(TagXelonForm, self).__init__(*args, **kwargs)
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
    item = forms.ChoiceField(choices=ITEM_CHOICES)
    custom_item = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'readonly': ''}), required=False)
    to = forms.CharField(max_length=5000, widget=forms.TextInput(), required=False)
    attach = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = Suptech
        fields = ['username', 'xelon', 'item', 'custom_item', 'time', 'to', 'info', 'rmq', 'attach']

    def __init__(self, *args, **kwargs):
        users = User.objects.all()
        _data_list = list(users.values_list('username', flat=True).distinct())
        super(SuptechModalForm, self).__init__(*args, **kwargs)
        self.fields['to'].initial = config.SUPTECH_TO_EMAIL_LIST
        if self.request.user:
            self.fields['username'].initial = self.request.user.username
        self.fields['username'].widget = ListTextWidget(data_list=_data_list, name='value-list')

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
        subject = f"!!! Info Support Tech : {self.instance.item} !!!"
        context = {"email": from_email, "suptech": self.instance, 'domain': current_site.domain}
        message = render_to_string('tools/email_format/suptech_request_email.html', context)
        email = EmailMessage(
            subject=subject, body=message, from_email=from_email,
            to=string_to_list(self.cleaned_data['to']), cc=[from_email]
        )
        files = self.request.FILES.getlist('attach')
        if files:
            for f in files:
                email.attach(f.name, f.read(), f.content_type)
        email.send()

    def save(self, commit=True):
        suptech = super(SuptechModalForm, self).save(commit=False)
        user = self.cleaned_data['username']
        suptech.date = timezone.now()
        suptech.user = f"{user.first_name} {user.last_name}"
        suptech.created_by = user
        suptech.created_at = timezone.now()
        if commit and not self.request.is_ajax():
            for field in ['username', 'custom_item', 'to', 'attach']:
                del self.fields[field]
            if self.cleaned_data['custom_item']:
                suptech.item = self.cleaned_data['custom_item']
            suptech.save()
            self.send_email()
            call_command('suptech')
        return suptech


class SuptechResponseForm(forms.ModelForm):
    action = forms.CharField(widget=forms.Textarea(), required=True)

    class Meta:
        model = Suptech
        fields = ['xelon', 'item', 'time', 'info', 'rmq', 'action']

    def send_email(self, request):
        subject = f"!!! Info Support Tech : {self.instance.item} !!!"
        context = {"user": request.user, "suptech": self.instance}
        message = render_to_string('tools/email_format/suptech_response_email.html', context)
        email = EmailMessage(
            subject=subject, body=message, from_email=request.user.email,
            to=[self.instance.created_by.email], cc=string_to_list(config.SUPTECH_TO_EMAIL_LIST)
        )
        email.send()

    def save(self, commit=True):
        suptech = super(SuptechResponseForm, self).save(commit=False)
        user = get_current_user()
        suptech.modified_by = user
        suptech.modified_at = timezone.now()
        if commit:
            suptech.save()
            call_command('suptech')
        return suptech
