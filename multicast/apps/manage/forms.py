from django import forms

from ..view.models import Stream


class EditForm(forms.ModelForm):
    class Meta:
        model = Stream
        fields = [
            "source_name",
            "description",
        ]
        labels = {
            "source_name": "Name of Originating Organization",
            "description": "Description of Stream",
        }
