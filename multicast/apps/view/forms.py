from django import forms

class DescriptionForm(forms.Form):
    ans = forms.CharField(widget=forms.TextInput, max_length=10000)
