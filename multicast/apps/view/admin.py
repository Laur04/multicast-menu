from django.contrib import admin

from .models import Description, Stream, Category, TrendingStream

admin.site.register(Category)
admin.site.register(Description)
admin.site.register(Stream)
admin.site.register(TrendingStream)
