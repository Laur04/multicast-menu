from django.contrib import admin

from .models import FailedQuery, ManualReport, StreamSubmission


admin.site.register(FailedQuery)
admin.site.register(ManualReport)
admin.site.register(StreamSubmission)
