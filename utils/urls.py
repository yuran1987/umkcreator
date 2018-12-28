from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'cut2pdf/$',views.convert2pdf, name='convert2pdf')
]