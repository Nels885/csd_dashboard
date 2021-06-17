from django.forms.utils import ErrorList
from django import forms
from django.core.files.images import get_image_dimensions
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group

from bootstrap_modal_forms.forms import BSModalModelForm
from .models import UserProfile, Post, WebLink, ShowCollapse


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

    def clean_image(self):
        avatar = self.cleaned_data['image']

        try:
            w, h = get_image_dimensions(avatar)

            # validate dimensions
            max_width = max_height = 150
            if w > max_width or h > max_height:
                raise forms.ValidationError(
                    'Please use an image that is %s x %s pixels or smaller.' % (max_width, max_height)
                )

            # validate content type
            main, sub = avatar.content_type.split('/')
            if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
                raise forms.ValidationError('Please use a JPEG, GIF or PNG image.')

            # validate file size
            if len(avatar) > (70 * 1024):
                raise forms.ValidationError('Avatar file size may not exceed 70k.')

        except AttributeError:
            """
            Handles case when we are updating the user profile
            and do not supply a new avatar
            """
            pass

        return avatar


class ShowCollapseForm(forms.ModelForm):

    class Meta:
        model = ShowCollapse
        exclude = ["user"]


class PostForm(BSModalModelForm):
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
        return user


class WebLinkForm(BSModalModelForm):
    class Meta:
        model = WebLink
        exclude = ['thumbnail']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5})
        }
