from django import forms

from bootstrap_modal_forms.forms import BSModalModelForm

from .models import SemRefBase


class RemanForm(BSModalModelForm):

    class Meta:
        model = SemRefBase
        fields = "__all__"


class UpdateRemanForm(RemanForm):

    class Meta:
        model = SemRefBase
        fields = "__all__"
        widgets = {
            'reman_reference': forms.TextInput(attrs={"readonly": ""})
        }
