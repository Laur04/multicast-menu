from django import forms

from ..view.models import Stream


# Allows submission of access codes to claim streams
class ClaimForm(forms.Form):
    access_code = forms.CharField(max_length=50, required=True)
