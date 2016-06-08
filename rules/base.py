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
    h=len(time)>2 and int(time[2])*60 or 0
    m=len(time)>1 and int(time[1])*60  or 0
    s=len(time)==1 and int(time[0]) or 0
    return h+m+s
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
class BaseData(object):

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
            self.user_plocation=map_info['user'] and map_info['user'].phone_place or u'unknow'
            self.user_phone= map_info['user_phone']
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

            self.init_contact()
            ptype=self.ext_api.get_phone_location(self.user_phone)
            if '移动' in ptype['supplier']:
                print '移动'
                self.init_sp_calldetail()
                self.init_sp_smsdetail()
                self.init_sp_netdetail()
                self.init_sp_recharege()
            elif '联通' in ptype['supplier']:
                print '联通'
                self.init_sp_unicom_calldetail()
                self.init_sp_unicom_smsdetail()
                self.init_sp_unicom_netdetail()
                self.init_sp_unicom_recharege()
            elif '电信' in ptype['supplier']:
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
        if not self.idcard or self.idcard == u'unknow':
            self.idcard_info = idcard_info_map
            return
        info = self.ext_api.get_info_by_id(self.idcard.cardno)
        b = info[2]
        age = (datetime.now()-datetime(int(b[:4]),int(b[4:6]),int(b[6:]))).days/365
        self.idcard_info={
            'sex':info[0],
            'home_location':info[1],
            'birthday':info[2],
            'age':age,
            'idcard':self.idcard.cardno
        }
            
    def init_sp_calldetail(self):
        phonedetail = self.sp and self.sp.phonedetail or {}
        mp=self.load_sp_datadetail(phonedetail)
        cmap={ c.phone:c.name for c in self.contacts }
        for k,v in mp.items():
            for itt in v:
                stime=k[:-2]+'-'+itt['startTime']      
                st=dd_start_time = datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')
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
        smsdetail = self.sp and self.sp.smsdetail or {}
        mp = self.load_sp_datadetail(smsdetail)
        cmap={ c.phone:c.name for c in self.contacts }
        for k,v in mp.items():
            for itt in v:
                stime=k[:-2]+'-'+itt['startTime']
                st=dd_start_time = datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')
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
        netdetail = self.sp and self.sp.netdetail or {}
        mp = self.load_sp_datadetail(netdetail)
        for k,v in mp.items():
            for itt in v:
                stime=k[:-2]+'-'+itt['startTime']
                st=dd_start_time = datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')
                n=UserNetInfo()
                n.owner_phone = self.user_phone
                n.start_time=st

                n.user_id = self.user_id

                n.comm_time = get_duration(itt['commTime'])
                n.sum_flow=itt['sumFlow']
                n.created_time = datetime.now()
                n.net_location=itt['commPlac']
                n.source=u'sp'
                n.net_type=itt['netType']
                self.sp_net.append(n)


    def init_sp_recharege(self):
        recharge = self.sp and self.sp.recharge or {}
        json_data = recharge
        mp = 'data' in json_data and json_data['data'] or {}
        charge_mp={}
        now=self.create_time
        for it in mp:
            td=it['payDate']
            key=datetime(int(td[0:4]),int(td[4:6]),int(td[6:8]),int(td[8:10]),int(td[10:12]),int(td[12:14]))
            if key>now-timedelta(180) and key<=now:
                charge_mp.update({
                    key:it['payFee']
                })
        self.sp_recharge = charge_mp

    def load_sp_datadetail(self,sp_map):
        mp={}
        for k,v in sp_map.items():
            itmp='data' in v and v['data'] or []
            for itt in itmp:
                if k not in mp:
                    mp[k]=[]
                mp[k].append(itt)
        return mp

    #联通
    def load_unicom_datadetail(self,sp_map):
        mp={}
        for k,v in sp_map.items():
            itmp = []
            if 'pageMap' in v and 'result' in v['pageMap']:
                itmp=v['pageMap']['result']
            for it in itmp:
                if k not in mp:
                    mp[k]=[]
                mp[k].append(it)
        return mp

    def init_sp_unicom_calldetail(self):
        phonedetail = self.sp and self.sp.phonedetail or {}
        mp=self.load_unicom_datadetail(phonedetail)
        cmap={ c.phone:c.name for c in self.contacts }
        for k,v in mp.items():
            for itt in v:
                stime=k[:-4]+'-'+ k[4:6] +'-' +k[6:] +' ' + itt['calltime']
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

        smsdetail = self.sp and self.sp.smsdetail or {}
        mp = self.load_unicom_datadetail(smsdetail)
        cmap={ c.phone:c.name for c in self.contacts }
        for k,v in mp.items():
            for itt in v:
                stime = k[:-4]+'-'+ k[4:6] +'-' + k[6:] +' ' + itt['smstime']
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

        netdetail = self.sp and self.sp.netdetail or {}
        mp = self.load_unicom_datadetail(netdetail)
        for k,v in mp.items():
            for itt in v:
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
        recharge = self.sp and self.sp.recharge or {}
        mp=self.load_unicom_datadetail(recharge)
        charge_mp={}
        now = self.create_time
        for k,v in mp.items():
            minv=0
            for itt in v:
                td=itt['paydate'].replace('-','')
                key=datetime(int(td[0:4]),int(td[4:6]),int(td[6:8]),random.randint(1,12))
                if key>now-timedelta(180) and key<=now:
                    charge_mp.update({
                        key : itt['payfee'].replace('-','')
                    })
        self.sp_recharge = charge_mp

    def init_contact(self):
        ucl = self.ucl
        if not ucl:
            return
        conlist = []
        try:
            conlist = ucl['linkmen']
        except:
            base_logger.error(get_tb_info())
            base_logger.error("【init contact error】"  + ",uid=" + self.user_id + ",datetime="+ str(datetime.now()))
        clist=[]
        for cc in conlist:
            itt=eval(cc)
            u = UserContact()
            u.name=itt['name'] and itt['name'].decode('utf8') or u''
            u.user_id = ucl['user_id']
            u.owner_phone=ucl["phone"]
            u.device_id = ucl["device_id"]
            u.source = str(itt['source'])
            u.created_at = datetime.now()
            u.phone =  format_phone(itt['contact_phone']) #号码规范
            g=self.ext_api.get_phone_location(u.phone)
            u.phone_location=g['province']+'-'+g['city']+'-'+g['supplier'] #手机归属地解析
            u.call_count = 0
            clist.append(u)
        self.contacts=clist

        #得到 含有有意义名字的通信录
        num_map = {}
        for c in self.contacts:
            if c.name.isdigit():
                continue
            if not self.ext_api.is_normal_phonenum(c.phone):
                continue
            if c.name in num_map:
                num_map[c.name].append(c)
            else:
                num_map[c.name] = [c]

        for k,v in num_map.items():
            if len(v) >=8:
                continue
            else:
                self.good_contacts.append(v)

        return
    

    def init_cmbcc(self):
        self.cb=None




      
    def init(self):
        base_logger.info("[  Init Begin ] orderid = "+self.order_id+",user_id = " +self.user_id)
        #profile
        self.sex, self.identity_location, self.identity_birth = self.ext_api.get_info_by_id(self.identity)
        #self.profile_change_log_list = ProfileChangeLog.objects.filter(user=self.user_id)

        self.self_phone_location = self.ext_api.get_phone_location(self.phone) 
        print "contacts,calls ,sms1"
        self.init_contact()
        print "contacts,calls ,sms2"
        self.init_calls()
        print "contacts,calls ,sms3"
        self.init_sms()

        print "init_system_info"
        self.init_system_info() 

        #sos user
        self.sos_user_list = self.get_sos_user()

        return 
