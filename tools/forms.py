from django import forms
from django.utils.translation import ugettext as _
from bootstrap_modal_forms.forms import BSModalForm

import re

from utils.export import calibre_file

from squalaetp.models import Xelon
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
        if re.match(r'^[a-zA-Z]\d{9}$', str(data)):
            try:
                Xelon.objects.get(numero_de_dossier=data)
            except Xelon.DoesNotExist:
                self.add_error('xelon', _('Xelon number no exist'))
        else:
            self.add_error('xelon', _('Xelon number is invalid'))
        return data

    def save(self, commit=True):
        xelon = self.cleaned_data['xelon']
        comments = self.cleaned_data['comments']
        calibre_file(comments, xelon, self.request.user.username)
        tag = super(TagXelonMultiForm, self).save(commit=False)
        tag.created_by = self.request.user
        if commit:
            tag.save()
        return tag
