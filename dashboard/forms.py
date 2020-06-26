from django.forms.utils import ErrorList
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group

from bootstrap_modal_forms.forms import BSModalForm

from .models import UserProfile, Post


class ParaErrorList(ErrorList):

    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ''
        return '<div>%s</div>' % ''.join(['<p class="text-danger">* %s</p>' % e for e in self])


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']


class PostForm(BSModalForm):
    class Meta:
        model = Post
        fields = ['title', 'overview']


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class SignUpForm(UserCreationForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=False)
    password1 = None
    password2 = None

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'group']
        widgets = {
            'email': forms.EmailInput(attrs={'required': True})
        }

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        clean_email = self.cleaned_data["email"]
        user.email = clean_email
        if commit:
            user.save()
            UserProfile(user=user).save()
        return user
