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

'''时间化'''
def data_format_sixmonth():
    mp={}
    dt = datetime.now().date()
    for i in range(0,6):
        st = dt-timedelta(i*30+15)
        key = st.month<10 and '0'+str(st.month) or str(st.month)
        mp[key] = str(st.year)
    return mp
'''自定义过滤字符串'''
def self_replace(argstr,valid_list = [0],target='-'):
    return not argstr and argstr not in valid_list and target or argstr

'''标题'''
def title_info(cmbd):
    mp=cmbd or None
    ct = str(datetime.now())
    if not mp:
        return {'phone_no':'-','ct':ct,'ptype':u'联通'}
    return {'phone_no':mp['phone_no'] or '-','ct':ct,'ptype':u'移动'}


'''个人信息'''
def basic_info(cmbd,score='-'):

    user_info = cmbd and cmbd.personalInfo or {}
    user_info_keys=['address','contactNum','email',
        'inNetDate','level','name''netAge',
        'realNameInfo','starLevel','starScore',
        'starTime','status','vipInfo','zipCode'
    ]

    phone_info =cmbd and cmbd.currRemainingAmount or {}
    phone_info_keys=['curFee','curFeeTotal','oweFee','realFee']


    rsmap={}
    #基本信息
    rsmap.update( 
        { k : v or '-' for k,v in user_info.items() if k in user_info_keys } 
        or { it : '-' for it in user_info_keys }
    )
    #手机信息
    rsmap.update( 
        { k : v or '-' for k,v in phone_info.items() if k in phone_info_keys }
        or { it : '-' for it in phone_info_keys }
    )
    #信用分数
    rsmap.update( {'credit_score' : score} )
    return rsmap



'''月固定套餐信息'''
def his_bill_info(cmbd):
    bill_list = cmbd and cmbd.historyBillInfo or {}
    bill_keys = [u'mealName', u'buckleFeTime', u'remark', u'fee', u'disposable']
    return bill_list or {'---':[{ it:'-' for it in bill_keys }]}

    
'''上网痕迹'''
def net_info(cmbd):
    #得到年月
    date_mp=data_format_sixmonth()
    net_list = cmbd and cmbd.netdetail or []
    net_keys = [ 'commFee','commPlac','commTime',
        'meal','netPlayType','netType','startTime','sumFlow'
    ]
    rs_map = {}    
    for it in net_list:
        if 'startTime' not in it:
            continue
        key = it['startTime'].split('-')[0]
        if key not in date_mp:
            continue
        kk = date_mp[key]+key
        if kk not in rs_map:
            rs_map[kk] = []
        rs_map[kk].append({ k:self_replace(v) for k,v in it.items() if k in net_keys})        
    

    return rs_map or {'---':[{ it:'-' for it in net_keys }]}

'''通话记录'''
def call_info(cmbd):
    #得到年月
    date_mp=data_format_sixmonth()
    
    phone_list = cmbd and cmbd.phonedetail or []
    phone_keys = [ 'anotherNm','commFee','commMode',
        'commPlac','commTime','commType',
        'mealFavorable','startTime'
    ]
    rs_map = {}
    for it in phone_list:
        key = it['startTime'].split('-')[0]
        if key not in date_mp:
            continue
        kk = date_mp[key]+key
        if kk not in rs_map:
            rs_map[kk] = []
        rs_map[kk].append({ k:self_replace(v) for k,v in it.items() if k in phone_keys })
    return rs_map or {'---' : [{ it:'-' for it in phone_keys }] }

'''短信记录'''
def sms_info(cmbd):
    #得到年月
    date_mp=data_format_sixmonth()
    
    sms_list = cmbd and cmbd.smsdetail or []
    sms_keys = [
        'anotherNm','busiName','commFee',
        'commMode','commPlac','infoType',
        'meal','startTime'
    ]
    rs_map = {}
    for it in sms_list:
        key = it['startTime'].split('-')[0]
        if key not in date_mp:
            continue
        kk = date_mp[key]+key
        if kk not in rs_map:
            rs_map[kk] = [] 
        #self_replace 过滤空字符串
        rs_map[kk].append({ k : self_replace(v) for k,v in it.items() if k in sms_keys })

    return rs_map or {'---':[{ it:'-' for it in sms_keys }]}

'''话费充值记录'''
def incharge(cmbd):
    recharge = cmbd and cmbd.recharge or []
    rsd_keys = [ 'payDate','payFee','payTypeName']
    return recharge or [ {it:'-' for it in rsd_keys} ]
'''开放式套餐'''
def open_business_info(cmbd):
    b_list =  cmbd and cmbd.openBusiness or []
    b_keys=[ 'busiName','effectTime','extinctTime','orderedTime']
    return map(lambda x:{k:self_replace(v) for k,v in x.items() if k in b_keys },b_list) or [{it:'-' for it in b_keys}]
def get_cb_infos(cmbd):
    return {
        'title' : title_info(cmbd),#标题
        'basicinfo' : basic_info(cmbd,score='-'),#基本信息
        'billinfo' : his_bill_info(cmbd),#月固定套餐信息
        'openbuss' : open_business_info(cmbd),#开放式套餐
        'netinfo' : net_info(cmbd),#上网痕迹
        'callinfo' : call_info(cmbd),#通话记录
        'recharge' : incharge(cmbd),#话费充值记录
        'smsinfo' : sms_info(cmbd),#短信记录
    }    
