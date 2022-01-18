from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address

from ..view.models import Stream
from .models import ManualReport


# Allows authenticated users to upload a file to be streamed
class AddByFileForm(forms.Form):
    file_to_stream = forms.FileField(allow_empty_file=False, required=True)


# Allows authenticated users to specify a link to get a video file from
class AddByLiveForm(forms.Form):
    link_to_stream = forms.URLField(required=True)


# Allows authenticated users to manually report a stream
class AddByManualForm(forms.ModelForm):
    class Meta:
        model = ManualReport
        fields = [
            "source",
            "group",
            "udp_port"
        ]

    def is_valid(self):
        valid = super(AddByManualForm, self).is_valid()
        source = self.cleaned_data["source"]
        group = self.cleaned_data["group"]

        unique = not Stream.objects.filter(source=source, group=group).exists()
        if not unique:
            self.add_error("source", "This stream already exists.")
            self.add_error("group", "This stream already exists.")
            valid = False

        try:
            validate_ipv4_address(source)
        except ValidationError:
            self.add_error("source", "Please enter a valid IPv4 address.")
            valid = False

        try:
            validate_ipv4_address(group)
        except ValidationError:
            self.add_error("group", "Please enter a valid IPv4 address.")
            valid = False

        if not self.cleaned_data["udp_port"].isdigit():
            self.add_error("udp_port", "Please enter an integer.")
            valid = False

        return valid
