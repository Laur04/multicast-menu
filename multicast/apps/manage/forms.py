from django import forms


class EditForm(forms.ModelForm):
    class Meta:
        fields = [
            "source_name",
            "description",
        ]
        labels = {
            "source_name": "Name of Originating Organization",
            "description": "Description of Stream",
        }
