from django import forms

class AddForm(forms.Form):
    source = forms.CharField(max_length=50, required=True)
    group = forms.CharField(max_length=50, required=True)
    description = forms.CharField(widget=forms.Textarea, max_length=10000)

class DescriptionForm(forms.Form):
    ans = forms.CharField(widget=forms.Textarea, max_length=10000)
