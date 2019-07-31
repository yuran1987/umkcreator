from django.conf.urls import url
from django.contrib.auth.decorators import login_required as auth
from . import views

urlpatterns = [
    url(r'import/(?P<type>(\w+))$', views.run_import_pubs, name='import_publications'),
    url(r'get/$', views.get_pubs_count, name='get_publications'),


]