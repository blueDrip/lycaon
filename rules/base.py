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
from datetime import datetime
from rules.util.utils import get_tb_info
from rules.raw_data import jingdong,liantong,yidong,UserCallPhone,UserShortMessage,UserNetInfo,UserContact
from rules.ext_api import EXT_API


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
    if "+86" == phone[:3]:
        phone = phone[3:]
    elif '86' == phone[:2]:
        phone = phone[2:]
    elif '+0086'== phone[:5]:
        phone = phone[5:]
    elif '0086' == phone[:4]:
        phone = phone[4:]
    return phone

class BaseData(object):

    """Docstring for OrderInfo. """
    def __init__(self,oid,ext=None):
        #try:
            '''user info'''
            self.user=None
            self.user_plocation=u'北京'
            self.home_location = u'江西南昌市'
            self.user_phone=u'15600300721'
            self.username=u'李超'
            
            self.create_time=datetime.now()          
            self.ext_api = ext or EXT_API()
            '''sp info'''
            self.sp=yidong.objects.filter()[2]
            self.sp_calls=[]
            self.good_calls=[]
            self.sp_sms=[]
            self.sp_net=[]
            '''JD info'''
            self.jd=jingdong.objects.filter(jd_login_name=str("lcswr@126.com")).first()
            '''contact info'''
            self.contacts = []
            self.good_contacts = []
            self.calls = []
            self.sms = []

            self.init_contact()
            self.init_sp_calldetail()
            self.init_sp_smsdetail()
            self.init_sp_netdetail()
        #except:
        #    print get_tb_info()
        #    base_logger.error(get_tb_info())
    def init_sp_calldetail(self):
        mp = self.load_sp_datadetail(self.sp.phonedetail)
        cmap={ c.phone:c.name for c in self.contacts }
        for k,v in mp.items():
            for itt in v:
                stime=k[:-2]+'-'+itt['startTime']      
                st=dd_start_time = datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')
                uc=UserCallPhone()
                uc.call_time = st
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
        #存库
        UserCallPhone.create_calls(self.sp_calls)
    def init_sp_smsdetail(self):
        mp = self.load_sp_datadetail(self.sp.smsdetail)
        cmap={ c.phone:c.name for c in self.contacts }
        for k,v in mp.items():
            for itt in v:
                stime=k[:-2]+'-'+itt['startTime']
                st=dd_start_time = datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')
                s=UserShortMessage()
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
        #存库
        UserShortMessage.create_smses(self.sp_sms)

    def init_sp_netdetail(self):
        mp = self.load_sp_datadetail(self.sp.netdetail)
        for k,v in mp.items():
            for itt in v:
                stime=k[:-2]+'-'+itt['startTime']
                st=dd_start_time = datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')
                n=UserNetInfo()
                n.owner_phone = self.user_phone
                n.start_time=st
                n.comm_time = get_duration(itt['commTime'])
                n.sum_flow=itt['sumFlow']
                n.created_time = datetime.now()
                n.net_location=itt['commPlac']
                n.source=u'sp'
                n.net_type=itt['netType']
                self.sp_net.append(n)
        #存库
        UserNetInfo.create_nets(self.sp_net)

    def load_sp_datadetail(self,sp_map):
        mp={}
        for k,v in sp_map.items():
            d=re.findall(r"\((.+)\).*",v)
            for it in d:
                itmp=json.loads(it)['data']
                for itt in itmp:
                    if k not in mp:
                        mp[k]=[]
                    mp[k].append(itt)
        return mp

            
   
    def init_contact(self):
        ucl = UserContact.objects.filter(owner_phone=u'18204315019')
        self.contacts =  [c for c in ucl]
        #更新手机归属地
        for c in self.contacts:
            # c.phone = normalize_num(c.phone)
            c.name=c.name.replace(' ','')
            c.phone = format_phone(c.phone)
            g = self.ext_api.get_phone_location(c.phone)
            c.phone_location = g['province'] + "-" + g['city'] + "-" + g['supplier']
            try:
                c.save()
            except:
                base_logger.error(get_tb_info())
                base_logger.error("SaveContactError" + c.phone + ",uid=" + self.user_id)
                continue
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

       



    #添加短信和电话中的联系人到通讯录中
#    def init_contact(self,userid):
        #source:  0:来着短信  1:来自通话记录  其他：来自通讯记录     
#        contact_list=[]
#        cmap={}
#        #print userid
#        #通讯录
#        cl=UserContact.objects.filter(owner_id=userid)
#        for c in cl:
#            #过滤位数小于六位的号码
#            if c.phone and len(c.phone)>6:
#                self.original_contacts.append(c)
#                contact_list.append(c)
#
#        #通话
#        ul=UserPhoneCall.objects.filter(owner_id=userid) 
#        for u in ul:
#            try:
#                name=u.name
#                if u.phone and not u.phone in cmap.keys():
#                    if name and u.phone[0]=='1' and len(u.phone)==11:
#                        cmap[u.phone]=u.phone
#                        uc=UserContact()
#                        uc.phone=u.phone
#                        uc.phone_location=u.phone_location
#                        uc.name=name
#                        uc.source=str(1)
#                        contact_list.append(uc)
#            except:
#                base_logger.error(get_tb_info())                     
#                continue
#        #短信
#        ml=UserShortMessage.objects.filter(owner_id=userid)
#        for it in ml:
#            try:
#                name=it.name
#                if it.phone and not it.phone in cmap.keys():
#                    if name and it.phone[0]=='1' and len(it.phone)==11:
#                        cmap[it.phone]=it.phone
#                        uc=UserContact()
#                        uc.phone=it.phone
#                        uc.phone_location=it.phone_location
#                        uc.name=it.name
#                        uc.source=str(0)
#                        contact_list.append(uc)
#            except:
#                base_logger.error(get_tb_info())
#                continue
#        #过滤电话号码
#        normal_contacts=[]
#        for c in contact_list:
#            #print c.phone
#            flag=self.ext_api.is_normal_phonenum(c.phone)
#            if flag:
#                normal_contacts.append(c)
#        #self.contacts = contact_list
#        self.contacts = normal_contacts
#
#    def test_init(self):
#        self.init_contact(self.user_id)
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
