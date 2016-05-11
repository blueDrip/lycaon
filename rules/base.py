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
from rules.raw_data import jingdong,liantong,yidong,UserCallPhone,UserShortMessage,UserNetInfo
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
class BaseData(object):

    """Docstring for OrderInfo. """
    def __init__(self,oid,ext=None):
        #try:
            '''user info'''
            self.user=None
            self.user_plocation='北京'
            self.home_location = '江西南昌市'
            self.user_phone=u'15600300721'

            
            self.create_time=datetime.now()          
            self.ext_api = ext or EXT_API()
            '''sp info'''
            self.sp=yidong.objects.filter()[20]
            self.sp_calls=[]
            self.good_calls=[]
            self.sp_sms=[]
            #self.init_sp_smsdetail()
            self.sp_net=[]
            #self.init_sp_netdetail()
            '''JD info'''
            self.jd=jingdong.objects.filter(jd_login_name=str("lcswr@126.com")).first()
            '''contact info'''
            self.contacts = []
            self.good_contacts = []
            self.calls = []
            self.good_calls = []
            self.sp_good_calls = []
            self.sms = []
            self.good_sms = []
            

            self.init_sp_calldetail()
            self.init_sp_smsdetail()
            self.init_sp_netdetail()
        #except:
        #    print get_tb_info()
        #    base_logger.error(get_tb_info())
    def init_sp_calldetail(self):
        mp = self.load_sp_datadetail(self.sp.phonedetail)
        for k,v in mp.items():
            for itt in v:
                stime=k[:-2]+'-'+itt['startTime']      
                st=dd_start_time = datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')
                uc=UserCallPhone()
                uc.call_time = st
                uc.phone=itt['anotherNm']
                uc.create_time = datetime.now()
                uc.location=itt['commPlac']
                phone=itt['anotherNm'][:2]==u'86' and itt['anotherNm'][2:] or itt['anotherNm']
                phone=phone[:4]==u'0086' and phone[4:] or phone    
                g=self.ext_api.get_phone_location(phone.replace(' ',''))
                uc.phone_location = g['province']+'-'+g['city']+'-'+g['supplier']
                uc.call_duration=get_duration(itt['commTime'])
                uc.source=u'sp'
                uc.call_type=itt['commMode']
                self.sp_calls.append(uc)
        #存库
        UserCallPhone.objects.filter().delete()
        UserCallPhone.create_calls(self.sp_calls)
    def init_sp_smsdetail(self):
        mp = self.load_sp_datadetail(self.sp.smsdetail)
        for k,v in mp.items():
            for itt in v:
                stime=k[:-2]+'-'+itt['startTime']
                st=dd_start_time = datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')
                s=UserShortMessage()
                s.send_time = st
                s.phone=itt['anotherNm']
                s.create_time = datetime.now()
                s.location=itt['commPlac']
                phone=itt['anotherNm'][:2]==u'86' and itt['anotherNm'][2:] or itt['anotherNm']
                phone=phone[:4]==u'0086' and phone[4:] or phone
                g=self.ext_api.get_phone_location(phone.replace(' ',''))
                s.phone_location = g['province']+'-'+g['city']+'-'+g['supplier']
                s.source=u'sp'
                s.sms_type=itt['commMode']
                self.sp_sms.append(s)
        #存库
        UserShortMessage.objects.filter().delete()
        UserShortMessage.create_smses(self.sp_sms)

    def init_sp_netdetail(self):
        mp = self.load_sp_datadetail(self.sp.netdetail)
        for k,v in mp.items():
            for itt in v:
                stime=k[:-2]+'-'+itt['startTime']
                st=dd_start_time = datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')
                n=UserNetInfo()
                n.owner_id=''
                n.username=''
                n.start_time=st
                n.comm_time = get_duration(itt['commTime'])
                n.sum_flow=itt['sumFlow']
                n.create_time = datetime.now()
                n.net_location=itt['commPlac']
                n.source=u'sp'
                n.net_type=itt['netType']
                self.sp_net.append(n)
        #存库
        UserNetInfo.objects.filter().delete()
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


            
    '''def init_sp_info(self):
           
        try:
            szro = get_sp_info(self.order_id) 
            call_map = {}
            save_list = []
            
            for c in self.calls:
                if c.phone + c.source + str(c.calling_time) not in call_map:
                    call_map[c.phone + c.source + str(c.calling_time)] =1
            if szro:
                dd = json.loads(szro.data)
                
                if 'operator_protype_data' in dd :
                    #print dd['operator_protype_data']['base_info']['userinfo']
                    self.sp_id=dd['operator_protype_data']['_id']
                    self.sp_update_time = dd['operator_protype_data']['update_time']
                    self.sp_userinfo_dict = dd['operator_protype_data']['base_info']['userinfo']
                
                dl = dd['operator_protype_data']['call_info']
                for month in dl:
                    for k,v in month.items():
                        for record in v['detail']:
                            try:
                                ucl = UserPhoneCall()
                                ucl.owner_id = self.user_id
                                ucl.phone = get_only_num(record['another_nm'])
                                #uc.phone = record['another_nm']
                                if 'comm_plac' in record:
                                    ucl.location = record['comm_plac'] 
                                else:
                                    ucl.location = 'ERROR'

                                ucl.type = 1 if '主叫' in record['comm_mode'] else 0
                                ucl.calling_duration = int(float(record['comm_time'])*60)

                                #print record['start_time']
                                #dd = time.strptime(record['start_time'],'%Y-%m-%d %H:%M:%S').date()
                            
                                dd_start_time = get_right_datetime(record['start_time'])
                                #dd_start_time = datetime.datetime.strptime(record['start_time'],'%Y-%m-%d %H:%M:%S')
                                #uc.calling_time = time.mktime(dd)*1000
                                ucl.calling_time = dd_start_time
                                #print type(uc.calling_time)
                                ucl.source = 'sp'
                                ucl.created_time = datetime.datetime.now()
                                if dd_start_time > ucl.created_time:
                                    y = int(record['start_time'].split('-')[0])
                                    y = y -1
                                    real_time_str = str(y) + '-'+'-'.join(record['start_time'].split('-')[1:])
                                    dd_start_time = datetime.datetime.strptime(real_time_str,'%Y-%m-%d %H:%M:%S')
                                    ucl.calling_time = dd_start_time

                                self.sp_calls.append(ucl)

                            except:
                                base_logger.error("SP_ERROR" +',id='+self.order_id)
                                print get_tb_info()
                                continue 
                #UserPhoneCall.create_calls(self.user_id,save_list,source='sp')
            return True
        except:
            self.error += "sp get error,"
            base_logger.error('SP_ERROR: '+get_tb_info())
            print get_tb_info()
            return False
    '''
    def init_contact(self):

        ucl = UserContact.objects.filter(owner_id=self.user_id)
        self.contacts =  [c for c in ucl]

        #更新手机归属地
        for c in self.contacts:
            # c.phone = normalize_num(c.phone)
            l = self.ext_api.get_phone_location(c.phone)
            c.phone_location = l['province'] + "-" + l['city'] + "-" + l['supplier']
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
            #if len(c.phone) <=6:
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


    def init_calls(self):

#        upcl = UserPhoneCall.objects.filter(owner_id=self.user_id)
#        self.calls = [c for c in upcl]

        #print 'changdu',len(self.calls)
        if self.profile.wecash_service_provider_authorized:
            self.init_sp_info()
            #upcl = UserPhoneCall.objects.filter(owner_id=self.user_id)
            #self.calls = [c for c in upcl]


        namemap = {c.phone:c.name  for c in self.contacts }
#        for c in self.calls:
#            if c.phone in namemap:
#                c.name = namemap[c.phone]

        for c in self.sp_calls:
            if c.phone in namemap:
                c.name = namemap[c.phone]

        num_map = {}
        sp_num_map = {}
        for c in self.sp_calls:
            if c.source =='sp':
                if c.phone in sp_num_map:
                    sp_num_map[c.phone].append(c)
                else:
                    sp_num_map[c.phone] = [c] 
        for c in self.calls:
            if c.phone in num_map:
                num_map[c.phone].append(c)
            else:
                num_map[c.phone] = [c] 


        self.good_calls = [ v for k,v in num_map.items()]
        self.sp_good_calls = [ v for k,v in sp_num_map.items()]

        print 'init calls1'
        for calls in self.good_calls:
            l = self.ext_api.get_phone_location(calls[0].phone)
            for c in calls:
                if c.phone_location =="":
                    c.phone_location = l['province'] + "-" + l['city'] + "-" + l['supplier']
#                    try:
#
#                        c.save()
#                    except NotUniqueError:
#                        continue
#
#                    except:
#                        base_logger.error("SaveCallError " + c.phone + ",uid=" + self.user_id + '  ' +get_tb_info())
#                        print get_tb_info()
#                        continue

        for calls in self.sp_good_calls:
            l = self.ext_api.get_phone_location(calls[0].phone)
            for c in calls:
                if c.phone_location =="":
                    c.phone_location = l['province'] + "-" + l['city'] + "-" + l['supplier']
#                    try:
#                        c.save()
#                    except NotUniqueError:
#                        continue
#                    except:
#                        base_logger.error("SaveCallError " + c.phone + ",uid=" + self.user_id + '  ' +get_tb_info())
#                        print get_tb_info()
#                        continue

        #write2redis(self.user_id,self.sp_calls)
        print 'init calls2'
        for calls in self.good_calls:
            calls.sort(key=lambda x:x.calling_time, reverse=True)    

        return 

#    def get_calls(self):
#        upcl = UserPhoneCall.objects.filter(owner_id=self.user_id)
#        self.calls = [for c in upcl]
#        num_map = {}
#        for c in self.calls:
#            if c.phone in num_map:
#                num_map[c.phone].append(c)
#            else:
#                num_map[c.phone] = [c] 
#
#        self.good_calls = [ v for k,v in num_map.items()]
#
#        for calls in self.good_calls:
#            calls.sort(key=lambda x:x.calling_time, reverse=True)    
#        return self.good_calls
       
    def init_sms(self):
        try:
            sl = UserShortMessage.objects.filter(owner_id=self.user_id)
            self.sms = [ s for s in sl ]
            num_map = {}
            for c in self.sms:
                if c.phone in num_map:
                    num_map[c.phone].append(c)
                else:
                    num_map[c.phone] = [c] 

            self.good_sms = [ v for k,v in num_map.items()]
                
            for ss in self.good_sms:
            # c.phone = normalize_num(c.phone)
                l = self.ext_api.get_phone_location(ss[0].phone)
     
                for c in ss:
                    c.phone_location = l['province'] + "-" + l['city'] + "-" + l['supplier']
#                    try:
#                        c.save()
#                    except:
#                        base_logger.error(get_tb_info())
#                        base_logger.error("SaveSmsError" + c.phone + ",uid=" + self.user_id)
#                        continue
        except:
            base_logger.error(get_tb_info())
            print get_tb_info()
        return 

    def init_system_info(self):
        try:
            #self.system_info_list = self.get_sys_list()
            self.system_info_list = self.get_sys_list()
            self.system_info = get_system_info_by_order(self.order)
            if self.system_info!=None:
                if is_ios(self.system_info.device_type):
                    self.device_type =0
                else:
                    self.device_type = 1
                self.gpslocation = self.system_info.gps
                if self.gpslocation =="":
                    gps = self.ext_api.get_gps_location_new(self.system_info.latitude,self.system_info.longitude)
                    self.gpslocation = gps['formatted_address']
                    self.system_info.gps = gps['formatted_address']
            #self.iplocation = self.ext_api.get_ip_location(self.system_info.ip)
                iplocation = self.ext_api.get_ip_location(self.system_info.ip)
                if iplocation != None:
                    self.system_info.iplocation = iplocation['country']+"-"+ iplocation['province'] +"-"+ iplocation['city']

                self.system_info.save()

        except:
            cu = Customer.objects.get(user=self.order.user)
            self.device_type = cu.device_type
            base_logger.error(get_tb_info()+",id="+self.order_id)
            print get_tb_info()+",id="+self.order_id
            self.system_info = None


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
        base_logger.info("[ Order Init Begin ] orderid = "+self.order_id+",user_id = " +self.user_id)
        #profile

        self.sex, self.identity_location, self.identity_birth = self.ext_api.get_info_by_id(self.identity)
        self.profile_change_log_list = ProfileChangeLog.objects.filter(user=self.user_id)

        self.self_phone_location = self.ext_api.get_phone_location(self.phone) 
#

#        ot = OrderTrace.create_order_trace(self.order)
#        if ot.sp_user_info !=""
#            self.sp_userinfo_dict = json.loads(ot.sp_user_info)
        #contacts,calls ,sms
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

    def get_sys_list(self):
        smap = {} 
        ot = self.order.created_time + datetime.timedelta(hours=8)
        ot = ot.replace(tzinfo=None)
        ot = ot - datetime.timedelta(days=30)

        try:
            cu = Customer.objects.get(user=self.order.user)
            sl = []
            if len(cu.device_id) > 5:
                sl = SystemInfo.objects.filter(device_id=cu.device_id,created_time__gt=ot)
            for s in sl:
                if str(s.id) not in smap:
                    smap[str(s.id)]= s
            
            sl = SystemInfo.objects.filter(user_id=str(self.order.user.id),device_id__ne='',created_time__gt=ot)
            for s in sl:
                if str(s.id) not in smap:
                    smap[str(s.id)]=s
            return [ v for k,v in smap.items() ]

        except:
            base_logger.error(get_tb_info())
            print get_tb_info()
            return []

    def get_sos_user(self):
        json_str = self.profile.urgent_contacts
        try:
            info = json.loads(json_str)
            sos_list = []
            for i in info:
                name_key = 'Name'
                phone_key = 'Phone'
                
                if 'name' in i:
                    name_key = 'name'
                    phone_key = 'phone'

                g = {}
                g['name'] = i[name_key]
                g['phone'] = i[phone_key].replace(' ','')
                g['relationship'] = i['Relationship']
                location = self.ext_api.get_phone_location(g['phone'])

                g['province'] =  location['province']
                g['city'] = location['city']
                sos_list.append(g)
            return sos_list
        except:
            base_logger.error(get_tb_info())

