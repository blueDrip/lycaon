from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url(r'api/user/^$', views.get_usercontact),
    url(r'^users/$', views.get_usercontact),
]
