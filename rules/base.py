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
from rules.raw_data import JdData,liantong,yidong,UserCallPhone,UserShortMessage,UserNetInfo,UserContact
from rules.raw_data import phonebook,cmbcc
from rules.ext_api import EXT_API
from rules.orm import tb_orm

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
            'user_id':None,
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
            #self.user=None
            #self.user_plocation=u'北京'
            #self.home_location = u'江西南昌市'
            #self.user_phone=u'15600300721'
            #self.username=u'李超'
            self.ext_api = ext or EXT_API()
            '''user info'''
            self.user = map_info['user']
            self.idcard = map_info['idcard']
            self.idcard_info={}
            self.user_plocation=map_info['user'] and map_info['user'].phone_place or u'unknow'
            self.user_phone=u'15600300721'
            self.username=u'李超'
            self.user_id = map_info['user_id']


            self.init_idcard_info()
            self.home_location = self.idcard_info['home_location']
            self.create_time=datetime.now()

            '''usercontact'''
            self.ucl = map_info['ucl']

            '''sp info'''
            #self.sp=yidong.objects.filter(phone_no=map_info['sp_login_name']).first()
            self.sp = map_info['sp']
            self.sp_calls=[]
            self.good_calls=[]
            self.sp_sms=[]
            self.sp_net=[]
            '''JD info'''
            #self.jd=jingdong.objects.filter(jd_login_name=map_info['jd_login_name']).first()
            self.jd = map_info['jd']
            #淘宝
            self.tb = tb_orm(cnd={"taobao_name" : "tb122917_00"})

            '''contact info'''
            self.contacts = []
            self.good_contacts = []
            self.calls = []
            self.sms = []

            '''creditCard'''
            self.cb = map_info['cb']

            self.init_contact()
            self.init_sp_calldetail()
            self.init_sp_smsdetail()
            self.init_sp_netdetail()
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
        mp = self.load_sp_datadetail(phonedetail)
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
        try:
            ul = UserCallPhone.objects.filter(user_id = self.user_id)
            if ul:
                self.sp_calls = ul
                print 'calls_list exist!'
            else:
                UserCallPhone.create_calls(self.sp_calls)
        except:
            base_logger.error(get_tb_info())
            base_logger.error("【init sp_calls error】"  + ",uid=" + self.user_id + ",datetime="+str(datetime.now()))
            print 'init sp_calls error'
            
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
        try:
            sms_list = UserShortMessage.objects.filter(user_id = self.user_id)
            if sms_list:
                self.sp_sms = sms_list
                print 'sp_sms exist'    
            else:
                UserShortMessage.create_smses(self.sp_sms)
        except:
            base_logger.error(get_tb_info())
            base_logger.error("【init sp_sms error】"  + ",uid=" + self.user_id + ",datetime="+str(datetime.now()))
            print 'init sp_sms error'
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
        try:
            net_list = UserNetInfo.objects.filter(user_id = self.user_id)
            if net_list:
                self.sp_net = net_list
                print 'net_list exist'
            else:
                UserNetInfo.create_nets(self.sp_net)
        except:
            base_logger.error(get_tb_info())
            base_logger.error("【init sp_net error】"  + ",uid=" + self.user_id + ",datetime="+str(datetime.now()))
            print 'init sp_net error'            

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
        #ucl = phonebook.objects.filter(user_id=u'111').first()
        ucl = self.ucl
        if not ucl:
            return
        conlist = []
        try:
            conlist = ucl['linkmen']
        except:
            base_logger.error(get_tb_info())
            base_logger.error("【init contact error】"  + ",uid=" + self.user_id + ",datetime="+datetime.now())
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
        try:
            u = UserContact.create_contacts(clist)
        except:
            base_logger.error(get_tb_info())
            base_logger.error("【SaveContactError】"  + ",uid=" + self.user_id)
            print 'SaveContactError'
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
        #self.cb = cmbcc.objects.filter(id=u'573ae5201d41c83f39423b9d').first()
        #cb_detail_list = cb and ab.detailBill or
        #for k,v in 
        self.cb=None

      
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
