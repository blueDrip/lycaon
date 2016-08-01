# coding=utf8
from corelib.database import MongoDb
from django.conf import settings
from sole_models.models import chinaUnicom_desplay,chinaMobile_desplay
from datetime import datetime


def china_unicom_orm_desplay(cnd={}):
    if 'None' in cnd.values():
        return None
    c=settings.APPXDB.get_collection('liantong').find_one(cnd,sort=[('createTime',-1)]) or {}
    if not c:
        return None
    cubd=chinaUnicom_desplay()
    cubd.rechargedetail = 'paymentRecord' in c and c['paymentRecord'] or {}
    cubd.historyBillInfo = 'historyBillInfo' in c and c['historyBillInfo'] or {}
    cubd.phonedetail = 'callDetail' in c and c['callDetail'] or {}
    cubd.netdetail = 'netDetail' in c and c['netDetail'] or {}
    cubd.smsdetail = 'smsDetail' in c and c['smsDetail'] or {}
    cubd.userinfo = 'userInfo' in c and c['userInfo'] or {}
    cubd.phoneInfo = 'phoneInfo' in c and c['phoneInfo'] or {}
    cubd.phone_no = c['phone_no']
    return cubd

def china_mobile_orm_desplay(cnd={}):
    if 'None' in cnd.values():
        return None
    c=settings.APPXDB.get_collection('yidong').find_one(cnd,sort=[('createTime',-1)]) or {}
    if not c:
        return None
    cmbd=chinaMobile_desplay()

    cmbd.currRemainingAmount = 'currRemainingAmount' in c and c['currRemainingAmount'] or {}
    cmbd.historyBillInfo = 'historyBillInfo' in c and c['historyBillInfo'] or {}
    cmbd.phonedetail = 'phoneDetail' in c and c['phoneDetail'] or {}
    cmbd.netdetail = 'netDetail' in c and c['netDetail'] or {}
    cmbd.smsdetail = 'smsDetail' in c and c['smsDetail'] or {}
    cmbd.personalInfo = 'personalInfo' in c and c['personalInfo'] or {}
    cmbd.openBusiness = 'openBusiness' in c and c['openBusiness'] or {}
    cmbd.phone_no = c['phone_no']
    cmbd.recharge = 'paymentRecord' in c and c['paymentRecord'] or {}

    return cmbd
