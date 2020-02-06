from django.forms.utils import ErrorList
from django.forms import ModelForm, TextInput, Select, DateInput, CharField, EmailField
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from bootstrap_modal_forms.mixins import PopRequestMixin, CreateUpdateAjaxMixin

from .models import CsdSoftware, UserProfile


class ParaErrorList(ErrorList):

    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ''
        return '<div>%s</div>' % ''.join(['<p class="text-danger">* %s</p>' % e for e in self])


class SoftwareForm(ModelForm):
    class Meta:
        model = CsdSoftware
        fields = [
            'jig', 'new_version', 'old_version', 'link_download', 'status', 'validation_date'
        ]
        widgets = {
            'jig': TextInput(attrs={'class': 'form-control'}),
            'new_version': TextInput(attrs={'class': 'form-control'}),
            'old_version': TextInput(attrs={'class': 'form-control'}),
            'link_download': TextInput(attrs={'class': 'form-control'}),
            'status': Select(attrs={'class': 'form-control'}),
            'validation_date': DateInput(attrs={'class': 'form-control'}),
        }


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class CustomUserCreationForm(PopRequestMixin, CreateUpdateAjaxMixin, UserCreationForm):
    first_name = CharField(max_length=30, required=False, help_text='Optional.')
    last_name = CharField(max_length=30, required=False, help_text='Optional.')
    email = EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
