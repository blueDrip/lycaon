#!/usr/bin/env python
# encoding: utf-8

import traceback
import socket
import time
import urllib

from mongoengine import (
    StringField, ListField, IntField, Document, EmbeddedDocumentField,
    DateTimeField, EmbeddedDocument, NotUniqueError, ReferenceField,
    BooleanField, PointField,
)

import  json
import re
import logging
import random
from datetime import datetime,timedelta
from rules.util.utils import get_tb_info
from rules.raw_data import UserCallPhone,UserShortMessage,UserNetInfo,UserContact
from rules.raw_data import phonebook,cmbcc
from rules.ext_api import EXT_API
from rules.orm import china_mobile_orm

base_logger = logging.getLogger('django.rules')
base_logger.setLevel(logging.INFO)

def get_right_datetime(string):

    dd_start_time = None
    try:
        dd_start_time = datetime.strptime(string,'%Y-%m-%d %H:%M:%S')
    except:
        try:
            aa = string[5:]
            dd_start_time = datetime.strptime(aa,'%Y/%m/%d %H:%M:%S')
        except:
            try:
                
                aa = string[5:]
                dd_start_time = datetime.strptime(aa,'%Y-%m-%d %H:%M:%S')
            except:
                base_logger.error(get_tb_info()+"SP_ERROR ")
                print get_tb_info()
                #raise SP_ERROR_Exception
    return dd_start_time
    
def get_duration(string):
    time=string.replace(u'小时',' ').replace(u'分',' ').replace(u'秒','').split(' ')
    h=len(time)>2 and int(time[2])*3600 or 0
    m=len(time)>1 and int(time[1])*60  or 0
    s=len(time)==1 and int(time[0]) or 0
    return h+m+s
def get_net_duration(string):
    time=string.split(':')
    return int(time[0])*3600+int(time[1])*60+int(time[2])
def format_phone(phone):
    phone = phone.replace('-','').replace(' ','')
    if u"+86" == phone[:3]:
        phone = phone[3:]
    elif u'86' == phone[:2]:
        phone = phone[2:]
    elif u'+0086'== phone[:5]:
        phone = phone[5:]
    elif u'0086' == phone[:4]:
        phone = phone[4:]
    return phone

class statBasedata(object):

    """Docstring for OrderInfo. 
        map_info = {
            'user':None,
            'user_id':str(None),
            'user_phone':None,
            'idcard':None,
            'jd':None,
            'tb':None,
            'sp':None,
            'cb':None,
        }
    """
    def __init__(self,map_info={},ext=None):
        try:
            '''user info'''
            self.ext_api = ext or EXT_API()
            '''user info'''
            self.user = map_info['user']
            self.idcard = map_info['idcard']
            self.idcard_info={}
            
            self.user_phone = map_info['user_phone']
            phone_info = self.ext_api.get_phone_location(self.user_phone)
            self.user_plocation = map_info['user'] and map_info['user'].phone_place or phone_info['province']+phone_info['city']

            self.username = u'none'
            self.user_id = map_info['user_id']


            self.init_idcard_info()
            self.home_location = self.idcard_info['home_location']
            self.create_time=datetime.now()

            '''usercontact'''
            self.ucl = map_info['ucl']

            '''sp info'''
            self.sp = map_info['sp']
            self.sp_calls=[]
            self.good_calls=[]
            self.sp_sms=[]
            self.sp_net=[]
            self.sp_recharge={}
            '''JD info'''
            self.jd = map_info['jd']
            #淘宝
            self.tb = map_info['tb']
            '''contact info'''
            self.contacts = []
            self.good_contacts = []
            self.calls = []
            self.sms = []

            '''creditCard'''
            self.cb = map_info['cb']

            '''授权sp数据的用户手机号'''
            sp_phone_info = self.sp and self.ext_api.get_phone_location(self.sp.userphone) or {'supplier':'none'}
            if '移动' in sp_phone_info['supplier']:
                print '移动'
                self.init_sp_calldetail()
                self.init_sp_smsdetail()
                self.init_sp_netdetail()
                self.init_sp_recharege()
            elif '联通' in sp_phone_info['supplier']:
                print '联通'
                self.init_sp_unicom_calldetail()
                self.init_sp_unicom_smsdetail()
                self.init_sp_unicom_netdetail()
                self.init_sp_unicom_recharege()
            elif '电信' in sp_phone_info['supplier']:
                pass
            else:
                pass
            #self.init_cmbcc()

        except:
            print get_tb_info()
            base_logger.error(get_tb_info())

    def init_idcard_info(self):
        idcard_info_map={ 'sex':u'unknow',
            'age':'unknow',
            'home_location':u'unknow',
            'birthday':u'unknow',
            'idcard':u'unknow'
        }
        #print self.idcard.cardno
        if not self.idcard or self.idcard == u'None':
            self.idcard_info = idcard_info_map
            return
        info = self.ext_api.get_info_by_id(self.idcard)
        b = info[2]
        age = (datetime.now()-datetime(int(b[:4]),int(b[4:6]),int(b[6:]))).days/365
        self.idcard_info={
            'sex':info[0],
            'home_location':info[1],
            'birthday':info[2],
            'age':age,
            'idcard':self.idcard
        }
    def init_sp_calldetail(self):
        phonedetail = self.sp and self.sp.phonedetail or []
        mp=self.load_sp_datadetail()
        cmap={ c.phone:c.name for c in self.contacts }
        phone_info = self.ext_api.get_phone_location(self.sp.userphone)
        for itt in phonedetail:
                stime=mp[itt['startTime'].split('-')[0]]+'-'+itt['startTime']     
                st = datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')
                uc=UserCallPhone()
                uc.call_time = st

                uc.user_id = self.user_id

                uc.owner_phone = self.user_phone
                uc.phone=itt['anotherNm']
                uc.username = uc.phone in cmap and cmap[uc.phone] or u'none'
                uc.created_time = datetime.now()
                uc.location=itt['commPlac']
                g=self.ext_api.get_phone_location(format_phone(uc.phone))
                uc.phone_location = g['province']+'-'+g['city']+'-'+g['supplier']
                uc.call_duration=get_duration(itt['commTime'])
                uc.source=u'sp'
                uc.call_type=itt['commMode']
                self.sp_calls.append(uc)
            
    def init_sp_smsdetail(self):
        smsdetail = self.sp and self.sp.smsdetail or []
        mp = self.load_sp_datadetail()
        cmap={ c.phone:c.name for c in self.contacts }
        for itt in smsdetail:
                stime=mp[itt['startTime'].split('-')[0]]+'-'+itt['startTime']
                st = datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')
                s=UserShortMessage()
                s.user_id = self.user_id
                s.send_time = st
                s.phone=itt['anotherNm']
                s.owner_phone = self.user_phone
                s.username = s.phone in cmap and cmap[s.phone] or u'none'
                s.created_time = datetime.now()
                s.location=itt['commPlac']
                g=self.ext_api.get_phone_location(format_phone(s.phone))
                s.phone_location = g['province']+'-'+g['city']+'-'+g['supplier']
                s.source=u'sp'
                s.sms_type=itt['commMode']
                self.sp_sms.append(s)
    def init_sp_netdetail(self):
        netdetail = self.sp and self.sp.netdetail or []
        mp = self.load_sp_datadetail()
        for itt in netdetail:
                key = itt['startTime'].split('-')[0]
                if key not in mp:
                    continue
                stime=mp[key]+'-'+itt['startTime']
                st = datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')
                n=UserNetInfo()
                n.owner_phone = self.user_phone
                n.start_time=st
                n.user_id = self.user_id
                comm_time_list = itt['commTime'].split(':')
                n.comm_time = int(comm_time_list[0])*3600+int(comm_time_list[1])*60+int(comm_time_list[0])
                n.sum_flow=int(float((itt['sumFlow'].replace('KB',''))))
                n.created_time = datetime.now()
                n.net_location=itt['commPlac']
                n.source=u'sp'
                n.net_type=itt['netType']
                self.sp_net.append(n)

    def init_sp_recharege(self):
        recharge = self.sp and self.sp.recharge or []
        charge_mp={}
        now=self.create_time
        for it in recharge:
            td=it['payDate']
            key=datetime(int(td[0:4]),int(td[4:6]),int(td[6:8]),int(td[8:10]),int(td[10:12]),int(td[12:14]))
            if key>now-timedelta(180) and key<=now and u'充值' in it['payTypeName']:
                charge_mp.update({
                    key:it['payFee']
                })
        self.sp_recharge = charge_mp


    def load_sp_datadetail(self):
        mp={}
        dt = datetime.now().date()
        for i in range(0,6):
            st = dt-timedelta(i*30+15)
            key = st.month<10 and '0'+str(st.month) or str(st.month)
            mp[key] = str(st.year)
        return mp

    #联通
    def load_unicom_datadetail(self,sp_map):
        pass        

    def init_sp_unicom_calldetail(self):
        phonedetail = self.sp and self.sp.phonedetail or []
        cmap={ c.phone:c.name for c in self.contacts }
        for itt in phonedetail:
                stime=itt['calldate'] +' ' + itt['calltime']
                st=dd_start_time = datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')
                uc=UserCallPhone()
                uc.call_time = st
                uc.user_id = self.user_id
                uc.owner_phone = self.user_phone

                uc.phone=itt['othernum']
                uc.username = uc.phone in cmap and cmap[uc.phone] or u'none'
                uc.created_time = datetime.now()
                uc.location=itt['homearea']
                g=self.ext_api.get_phone_location(format_phone(uc.phone))
                uc.phone_location = g['province']+'-'+g['city']+'-'+g['supplier']
                uc.call_duration=get_duration(itt['calllonghour'])
                uc.source=u'sp'
                uc.call_type=itt['calltypeName']
                self.sp_calls.append(uc)

    def init_sp_unicom_smsdetail(self):

        smsdetail = self.sp and self.sp.smsdetail or []
        cmap={ c.phone:c.name for c in self.contacts }
        for itt in smsdetail:
                stime = itt['smsdate'] +' ' + itt['smstime']
                st=dd_start_time = datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')
                s=UserShortMessage()
                s.user_id = self.user_id
                s.send_time = st
                s.phone=itt['othernum']
                s.owner_phone = self.user_phone
                s.username = s.phone in cmap and cmap[s.phone] or u'none'

                s.created_time = datetime.now()
                s.location=itt['homearea']
                g=self.ext_api.get_phone_location(format_phone(s.phone))
                s.phone_location = g['province']+'-'+g['city']+'-'+g['supplier']
                s.source=u'sp'
                s.sms_type=itt['smstype']
                self.sp_sms.append(s)
                
    def init_sp_unicom_netdetail(self):

        netdetail = self.sp and self.sp.netdetail or []
        for itt in netdetail:
                stime=itt['begintime']
                st=dd_start_time = datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')
                n=UserNetInfo()
                n.owner_phone = self.user_phone
                n.start_time=st

                n.user_id = self.user_id

                n.comm_time = get_duration(itt['durationtime'])
                n.sum_flow = 0 
                n.created_time = datetime.now()
                n.net_location='' #根据ip解析itt['clientip']
                n.source=u'sp'
                n.net_type=itt['apn']
                self.sp_net.append(n)


    def init_sp_unicom_recharege(self):
        recharge = self.sp and self.sp.recharge or []
        charge_mp={}
        now = self.create_time
        for itt in recharge:
            td=itt['paydate'].replace('-','')
            key=datetime(int(td[0:4]),int(td[4:6]),int(td[6:8]),random.randint(1,12))
            if key>now-timedelta(180) and key<=now:
                charge_mp.update({
                    key : itt['payfee'].replace('-','')
                })
        self.sp_recharge = charge_mp
