from django.contrib import admin

from .models import ManualReport, StreamSubmission


admin.site.register(ManualReport)
admin.site.register(StreamSubmission)
