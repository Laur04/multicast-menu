from django import forms
from captcha.fields import CaptchaField

class AddForm(forms.Form):
    source = forms.CharField(max_length=50, required=True)
    group = forms.CharField(max_length=50, required=True)
    udp = forms.CharField(max_length=50, required=False)
    description = forms.CharField(widget=forms.Textarea, max_length=10000)
    email = forms.EmailField()

class DescriptionForm(forms.Form):
    ans = forms.CharField(widget=forms.Textarea, max_length=10000)

class EmailForm(forms.Form):
    sender = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, max_length=10000, required=True)
    captcha = CaptchaField()
