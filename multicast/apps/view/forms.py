from django import forms


# Allows submission of stream descriptions
class DescriptionForm(forms.Form):
    text = forms.CharField(widget=forms.TextInput, max_length=10000, required=True)
