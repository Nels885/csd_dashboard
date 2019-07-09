from django.forms.utils import ErrorList
from django.forms import ModelForm, TextInput, Select, DateInput

from .models import CsdSoftware


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
