from django import forms
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from bootstrap_modal_forms.forms import BSModalModelForm
from crum import get_current_user
from constance import config

from utils.conf import string_to_list
from utils.django.validators import validate_xelon

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
        ('Hot Line Tech', 'Hot Line Tech'), ('Support Admin', 'Support Admin'), ('R.M.', 'R.M.'),
        ('Temps Annexe', 'Temps Annexe'), ('Validation Tech', 'Validation Tech'),
        ('Retour Autotronik', 'Retour Autotronik'), ('Probleme process', 'Probleme process'),
        ('Informatique/Reseau', 'Informatique/Reseau'), ('Inter Maintenance(AF/YM)', 'Inter Maintenance(AF/YM)'),
        ('Autres... (Avec resumé)', 'Autres... (Avec resumé)')
    ]
    item = forms.ChoiceField(choices=ITEM_CHOICES)

    class Meta:
        model = Suptech
        fields = ['xelon', 'item', 'time', 'info', 'rmq']

    def send_email(self):
        subject = f"!!! Info Support Tech : {self.cleaned_data['item']} !!!"
        context = {"email": self.request.user.email, "suptech": self.instance}
        message = render_to_string('tools/email_format/suptech_email.html', context)
        email = EmailMessage(
            subject=subject, body=message, from_email=self.request.user.email,
            to=string_to_list(config.SUPTECH_TO_EMAIL_LIST), cc=[self.request.user.email]
        )
        email.send()

    def save(self, commit=True):
        suptech = super(SuptechModalForm, self).save(commit=False)
        user = get_current_user()
        suptech.date = timezone.now()
        suptech.user = f"{user.first_name} {user.last_name}"
        suptech.created_by = user
        suptech.created_at = timezone.now()
        if commit and self.request.is_ajax():
            suptech.save()
        return suptech
