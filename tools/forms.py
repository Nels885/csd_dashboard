from django import forms
from django.utils.translation import ugettext as _
from bootstrap_modal_forms.forms import BSModalForm

from utils.export import calibre_file
from utils.validators import validate_xelon

from .models import TagXelonMulti


class TagXelonMultiForm(BSModalForm):
    class Meta:
        model = TagXelonMulti
        fields = ['xelon', 'comments']
        widgets = {
            'xelon': forms.TextInput(attrs={'class': 'form-control col-sm-6'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        }

    def clean_xelon(self):
        data = self.cleaned_data['xelon']
        message = validate_xelon(data)
        if message:
            self.add_error('xelon', _(message))
        return data

    def save(self, commit=True):
        xelon = self.cleaned_data['xelon']
        comments = self.cleaned_data['comments']
        calibre_file(comments, xelon, self.request.user.username)
        tag = super().save(commit=False)
        tag.created_by = self.request.user
        if commit:
            tag.save()
        return tag
