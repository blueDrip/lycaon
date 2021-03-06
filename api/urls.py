from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url(r'api/user/^$', views.get_usercontact),
    #url(r'^users/$', views.get_usercontact),
    #url(r'^detail/$',views.credit_detail),
    #url(r'^userinfo/$',views.users_views),
    url(r'^login/$',views.admin_login_views),
    url(r'^rulesinfo/$',views.rules_detail_info),
    url(r'^reg/$',views.reg),
    url(r'^reback/$',views.reback),
    #url(r'^del/$',views.delitem),
    url(r'^score/',views.score_views),
    url(r'^index/',views.admin_index_views),
    url(r'^checkerr/',views.check_error_views),
    url(r'^stat/',views.stat_data_views),
    url(r'^feature/',views.choice_feature_views),
    url(r'^calbymodel/',views.cal_again_views),
    url(r'^sys/',views.set_sys_views),
    url(r'^role/',views.role_views),
    url(r'^ruleitems/',views.rules_items_vies),
    url(r'^deluser/',views.del_views),
    url(r'^chars/',views.stat_chars_views),
    url(r'^login_auth/',views.login_auth),
    url(r'^logout/',views.logout),
    url(r'^apache/',views.apache_views),
    url(r'^createuser/',views.create_user_views),
    url(r'^createrole/',views.create_role),
    url(r'^distrrole/',views.distr_role_to_user),
    url(r'^chagerole/',views.chagerole),
    url(r'^delsysuser/',views.del_sys_user),
    url(r'^checklog/',views.check_log),
    url(r'^spinfo/',views.sp_data_views),
    url(r'^saveitem/',views.save_event),
    url(r'^checkbase/',views.check_info_views),
            
]
