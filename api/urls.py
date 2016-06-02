from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url(r'api/user/^$', views.get_usercontact),
    #url(r'^users/$', views.get_usercontact),
    url(r'^detail/$',views.credit_detail),
    url(r'^userinfo/$',views.users_views),
    url(r'^login/$',views.admin_login_views),
    url(r'^rulesinfo/$',views.rules_detail_info),
]
