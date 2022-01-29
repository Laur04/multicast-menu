from django.contrib import admin

from .models import TranslationServer, TranslationServerSubmission


admin.site.register(TranslationServer)
admin.site.register(TranslationServerSubmission)
