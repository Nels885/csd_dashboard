from django.forms.utils import ErrorList
from django import forms
from django.utils.translation import gettext as _
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.files.images import get_image_dimensions
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
from django.conf import settings

from bootstrap_modal_forms.forms import BSModalModelForm
from .models import UserProfile, Post, WebLink, ShowCollapse, SuggestBox

from utils.django.forms.fields import ListTextWidget

SERVICE_CHOICES = [('', '---'), ('CO', 'CO'), ('CE', 'CE'), ('ADM', 'ADM')]
JOB_TITLE_CHOICES = [
    ('', '---'), ('technician', 'technician'), ('operator', 'operator'), ('animator', 'animator'),
    ('engineer', 'engineer'), ('manager', 'manager')
]


class ParaErrorList(ErrorList):

    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ''
        return '<div>%s</div>' % ''.join(['<p class="text-danger">* %s</p>' % e for e in self])


class UserProfileAdminForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['job_title', 'service', 'image']
        widgets = {
            'job_title': forms.Select(choices=JOB_TITLE_CHOICES),
            'service': forms.Select(choices=SERVICE_CHOICES)
        }

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


class UserProfileForm(UserProfileAdminForm):
    class Meta(UserProfileAdminForm.Meta):
        fields = ['image']


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
    group = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(), widget=FilteredSelectMultiple("Group", is_stacked=False), required=False)
    password1 = None
    password2 = None

    class Media:
        css = {
            'all': ('/static/admin/css/widgets.css', '/static/admin/css/overrides.css'),
        }
        extra = '' if settings.DEBUG else '.min'
        js = ('/jsi18n/',)

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


class SearchForm(forms.Form):
    SELECTS = [
        ('atelier', 'Atelier'), ('reman', 'Reman'), ('sivin', 'SIVIN')
    ]

    select = forms.ChoiceField(choices=SELECTS, widget=forms.Select())
    query = forms.CharField(widget=forms.TextInput(attrs={"placeholder": _("Search Xelon, VIN or SN...")}))


class SuggestBoxModalForm(BSModalModelForm):
    username = forms.CharField(max_length=50, required=True)

    class Meta:
        model = SuggestBox
        fields = ['username', 'title', 'description', 'objective']

    def __init__(self, *args, **kwargs):
        users = User.objects.all()
        _data_list = list(users.values_list('username', flat=True).distinct())
        super().__init__(*args, **kwargs)
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

    def save(self, commit=True):
        instance = super().save(commit=False)
        user = self.cleaned_data['username']
        instance.created_by = user
        if commit and not self.request.is_ajax():
            instance.save()
        return instance
