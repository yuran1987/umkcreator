from django.conf.urls import url
from django.contrib.auth.decorators import login_required as auth
from . import views

urlpatterns = [
    url(r'import/(?P<type>(\w+))$', auth(views.run_import_pubs), name='import_publications'),
    url(r'get/$', auth(views.get_pubs_count), name='get_publications'),
    url(r'gen/(?P<type>(\w+))$', auth(views.get_pubs_by_docx), name='get_publications_docx'),


]