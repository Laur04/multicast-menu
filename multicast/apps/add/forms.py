from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address

from ..view.models import Stream


class AddForm(forms.ModelForm):
    description = forms.CharField(max_length=10000, widget=forms.Textarea, required=True)

    class Meta:
        model = Stream
        fields = [
            "source",
            "group",
            "udp_port",
            "email"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["udp_port"].label = "UDP Port (optional)"
        self.fields["email"].label = "Contact Email"
        self.fields["email"].required = True

    def is_valid(self):
        valid = super(AddForm, self).is_valid()
        source = self.cleaned_data["source"]
        group = self.cleaned_data["group"]

        unique = not Stream.objects.filter(source=source, group=group).exists()
        if not unique:
            self.add_error('source', 'This stream already exists.')
            self.add_error('group', 'This stream already exists.')
            valid = False

        try:
            source_valid = validate_ipv4_address(source)
        except ValidationError:
            self.add_error('source', 'Please enter a valid IPv4 address.')
            valid = False

        try:
            group_valid = validate_ipv4_address(group)
        except ValidationError:
            self.add_error('group', 'Please enter a valid IPv4 address.')
            valid = False

        if self.cleaned_data["udp_port"] is not None and not self.cleaned_data["udp_port"].isdigit():
            self.add_error('udp_port', 'Please enter an integer.')
            valid = False

        return valid
