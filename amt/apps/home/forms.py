from django import forms

class AddForm(forms.Form):
    ip = forms.CharField(max_length=100, required=True)
