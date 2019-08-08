from django.contrib import admin
from .models import Publications


class PublicationsAdmin(admin.ModelAdmin):
    list_display = ('creator','authors', 'title','year', 'doi', 'cites', 'isScopusWoS')
    list_filter = ['year','creator']


admin.site.register(Publications,PublicationsAdmin)
