# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import M_Source, Stream, Description

admin.site.register(M_Source)
admin.site.register(Stream)
admin.site.register(Description)
