# coding=utf8
from corelib.database import MongoDb
from django.conf import settings
from sole_models.models import chinaUnicom_desplay
from datetime import datetime

#def china_mobile_orm(cnd={}):
#    if 'None' in cnd.values():
#        return None

#    #d=MongoDb('101.201.109.253',27017,'app_data','heigeMeixin','app_grant_data')
#    d=MongoDb('101.201.109.253',27017,'plat_data','plat_data','plat_grant_data')
#    c=d.get_collection('yidong').find_one(cnd,sort=[('createTime',-1)]) or {}


def china_unicom_orm_display(cnd={}):
    if 'None' in cnd.values():
        return None
    #d=MongoDb('101.201.109.253',27017,'app_data','heigeMeixin','app_grant_data')
    d=MongoDb('101.201.109.253',27017,'plat_data','plat_data','plat_grant_data')
    c=d.get_collection('liantong').find_one(cnd,sort=[('createTime',-1)]) or {}
    if not c:
        return None
    cubd=chinaUnicom_desplay()
    cubd.rechargedetail = c['paymentRecord']
    cubd.historyBillInfo = c['historyBillInfo']
    cubd.phonedetail = c['callDetail']
    cubd.netdetail = c['netDetail']
    cubd.smsdetail = c['smsDetail']
    cubd.userinfo = c['userInfo']
    cubd.phoneInfo = c['phoneInfo']
    cubd.phone_no = c['phone_no']
    return cubd
