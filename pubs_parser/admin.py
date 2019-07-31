from django.contrib import admin
from .models import Publications


class PublicationsAdmin(admin.ModelAdmin):
    list_display = ('authors', 'title','year',  'doi', 'cites')
    list_filter = ['year']


admin.site.register(Publications,PublicationsAdmin)
