# coding=utf8
import sys
import os
import django
#sys.setdefaultencoding('utf8')
if __name__ == '__main__':
    local_dir = sys.argv[1]
    sys.path.append(local_dir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lycaon.settings'
    django.setup()
from django.conf import settings
from django.db.models import Q,Sum,F
from rules.models import BaseRule

from mongoengine import (
     StringField, ListField, IntField, Document, EmbeddedDocumentField, FloatField,
     DateTimeField, EmbeddedDocument
)
import logging
import StringIO
import json
logger = logging.getLogger('django.rules')
logger.setLevel(logging.INFO)
import time
from datetime import datetime, date, timedelta

'''标题'''
def title_info(cubd):
    mp=cubd or None
    ct = str(datetime.now())
    if not mp:
        return {'phone_no':'-','ct':ct,'ptype':u'联通'}
    return {'phone_no':mp['phone_no'] or '-','ct':ct,'ptype':u'联通'}

'''个人信息'''
def basic_info(cubd,score='-'):

    user_info = cubd and cubd.userinfo or {}
    user_info_keys=[ 'userName','certType','sex','certAddr','certNum','email' ]

    phone_info =cubd and cubd.phoneInfo or {}
    phone_info_keys=[u'roamstat', u'brand', u'inNetDate', u'userStatus', 
        u'payType', u'realFee', u'phoneNumber', u'landLevel', 
        u'userLevel', u'totalCreditValue', u'totalScore', 
        u'balance', u'packageName'
    ]

    rsmap={}
    #基本信息
    rsmap.update( 
        { k : v or '-' for k,v in user_info.items()} 
        or { it : '-' for it in user_info_keys }
    )
    #手机信息
    rsmap.update( 
        { k : v or '-' for k,v in phone_info.items()}
        or { it : '-' for it in phone_info_keys }
    )
    #信用分数
    rsmap.update( {'credit_score' : score} )
    return rsmap



'''历史账单'''
def his_bill_info(cubd):
    bill_list = cubd and cubd.rechargedetail or {}
    



    
'''上网痕迹'''
def net_info(cubd):
    net_list = cubd and cubd.netdetail or []
    net_keys = [u'flowname', u'uptraffic', u'featinfo', 
        u'bizname', u'totaltraffic', u'biztype', 
        u'domainname', u'downtraffic', u'durationtime', 
        u'apn', u'begintime', u'accessip', u'flowtype', 
        u'useragent', u'clientip', u'rattype'
    ]
    return net_list or [ { it : '-' for it in net_keys} ]

'''通话记录'''
def call_info(cubd):
    phone_list = cubd and cubd.phonedetail or [{}]
    phone_keys = ['calldate','calllonghour','calltime','calltype',
        'calltypeName','cellid','deratefee','homearea','homeareaName',
        'homenum','landfee','landtype','longtype','nativefee','otherarea',
        'otherareaName','otherfee','othernum','roamfee','romatype',
        'romatypeName','thtype','thtypeName','totalfee','twoplusfee'
    ]
    return map(lambda x:{k:v for k,v in x.items() if k in phone_keys },phone_list) or [{ it:'-' for it in phone_keys }]
'''短信记录'''
def sms_info(cubd):
    sms_list = cubd and cubd.smsdetail or []
    sms_keys = [u'businesstype', u'fee', u'othernum', 
        u'smsdate', u'smstype', u'amount', 
        u'smstime', u'otherarea', u'homearea', u'deratefee'
    ]
    return map(lambda x:{k:v for k,v in x.items() if k in sms_keys },sms_list) or [{ it:'-' for it in sms_keys }]

'''话费充值记录'''
def incharge(cubd):
    recharge = cubd and cubd.rechargedetail or []
    rsd_keys = [u'paydate', u'payfee', u'paychannel']
    return recharge or [ {it:'-' for it in rsd_keys} ]
