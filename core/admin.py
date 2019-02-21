from django.contrib import admin
from .models import Ministerstvo, Discipline, Directions, Profiles, Plans, Univercity,Departaments,Units,UmkArticles, UmkData,Competence, User

# Register your models here.
class ProfilesAdmin(admin.ModelAdmin):
    list_display = ('direction','name')
    list_filter = ['name']


class PlansAdmin(admin.ModelAdmin):
    list_display = ('id','code_OPOP', 'get_direction','get_profiles','year',  'discipline', 'training_form', 'get_semestrs','get_trudoemkost_zach_ed', 'get_if_zachot_exam', 'check_trudoemkost')
    list_filter = ['discipline']

class UserAdmin(admin.ModelAdmin):
    list_display = ('username','deparmt','last_name', 'first_name','get_patronymic','get_position','email','get_is_superuser')

class CompetentceAdmin(admin.ModelAdmin):
    list_display = ('name','direction','training_program', 'qualif')
    list_filter = ['name']

class DisciplineAdmin(admin.ModelAdmin):
    list_filter = ['name']

admin.site.register(User,UserAdmin)
admin.site.register(Discipline,DisciplineAdmin)
admin.site.register(Directions)
admin.site.register(Competence,CompetentceAdmin)
admin.site.register(Profiles,ProfilesAdmin)
admin.site.register(Plans,PlansAdmin)
admin.site.register(Univercity)
admin.site.register(Ministerstvo)
admin.site.register(Departaments)
admin.site.register(Units)
admin.site.register(UmkArticles)
admin.site.register(UmkData)
