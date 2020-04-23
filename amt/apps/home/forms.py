from django import forms

class AddForm(forms.Form):
    ip = forms.CharField(max_length=100, required=True)

class DescriptionForm(forms.Form):
    ans = forms.CharField(widget=forms.Textarea, max_length=10000)
