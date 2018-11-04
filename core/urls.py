from django.conf.urls import url
from django.contrib.auth.decorators import login_required as auth
from . import views

urlpatterns = [
    url(r'^accounts/profile/(?P<slug>\w+)$',views.UserProfileDetailView.as_view(), name='profile'),
    url(r'^accounts/edit_profile/$',auth(views.UserProfileEditView.as_view()), name='edit_profile'),
    url(r'^accounts/password/change/auth_password_change_done$',views.User_password_changed),
    url(r'^about/',views.showAuthors, name='showAuthors'),
    url(r'^news/',views.showNews, name='showNews'),
    url(r'^systeminfo/', views.showSysInfo, name='showSystemInfo'),
    url(r'^umk/list/remove/(?P<id>(\d+))/$',views.remove_umk, name='umkremove'),
    url(r'^umk/list/',views.showUmkList, name='showumklist'),
    url(r'^umk/next/(?P<id>(\d+))/(?P<direct_id>(\d+))/(?P<tr_program>(\w+))$', views.actions, {'type': 'create'}, name='umk_create'),
    url(r'^umk/edit/(?P<id>(\d+))/core/$',views.DataForUmk_core, name='umk_edit_core'),
    url(r'^umk/edit/(?P<id>(\d+))/laborat/$',views.DataForUmk_addons, {'type': 'laborat'}),
    url(r'^umk/edit/(?P<id>(\d+))/prakt/$',views.DataForUmk_addons, {'type': 'prakt'}),
    url(r'^umk/edit/(?P<id>(\d+))/$',views.actions, {'type': 'actlist'}, name='umk_edit_menu'),
    url(r'^umk/edit/(?P<id>(\d+))/rating/$',views.show_rating, name='showrating'),
    url(r'^umk/edit/(?P<id>(\d+))/literature/$',views.show_liter, name='showliter'),
    url(r'^umk/edit/(?P<id>(\d+))/literature/get/(?P<type>(\w+))/(?P<search>[+\w]+)/$',views.get_literature_from_url, name='getliter'),
    url(r'^umk/get/(?P<id>(\d+))/(?P<format>[a-z]{3,4})/$', views.get_document),
    url(r'^umk/get/(?P<id_list>[+\d]+)/(?P<format>[a-z]{3,4})/$', views.get_document_in_archive),
    url(r'^umk/copy/', views.showUmkCopy, name='umkcopy'),
    url(r'^umk/send2sign/(?P<id>[+\d+]+)/$', views.send2signature, name='send2signtr'),
    url(r'^umk/zaf_kav_sign_list/$', views.showUmkForSignature, name='umklistsign'),
    url(r'^umk/zaf_kav_sign_confirm/(?P<id>[+\d+]+)/$', views.send2confirm, name='umklistconfirm'),
    url(r'^umk/create/',views.actions, {'type':'choiseDisp'}, name='umkcreate'),
    url(r'^plan/upload/',views.uploadplan, name='planupload'),
    url(r'^plan/list/',views.showPlansAll, name='planlist'),
    url(r'^plan/remove/(?P<id>(\d+))/$',views.removePlan, name='planremove'),
    url(r'^competence/upload/',views.uploadcompetence, name='uploadcompetence'),
    url(r'^$', views.index, name = 'index.html'),
]