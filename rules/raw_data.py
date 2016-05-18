# coding=utf8
import sys
reload(sys)
# Create your models here.
import datetime
from mongoengine import (
    StringField, IntField, Document, DateTimeField, BooleanField,
    ObjectIdField,ListField,ListField,ReferenceField,FloatField,NotUniqueError,
    EmbeddedDocument,
)
import traceback
from django.db import models
from django.conf import settings
 
#用户通讯录

class UserContact(Document):
    phone = StringField(required = True,unique_with=['user_id', 'name'])
    user_id = StringField(required = True)
    owner_phone = StringField(required = True)
    created_time = DateTimeField()
    phone_location = StringField(default=str)
    source = StringField(default=str) #usercontact来源 1:通讯录，2.sp
    created_at = DateTimeField()  # 手机内创建时间
    name = StringField(default = str)
    call_count = IntField(default=int)
    device_id = StringField(default=str)

    meta = {
        "indexes": [
            'phone', 'user_id', '-created_time', 'device_id'
        ],
        'index_background': True
    }

    @classmethod
    def create_contact(cls,data,need_save=True):
        c = cls()
        c.phone = data.phone
        c.user_id = data.user_id
        c.owner_phone = data.owner_phone
        c.created_time = datetime.datetime.now()
        c.phone_location = data.phone_location
        c.source = data.source         #usercontact来源 1:通讯录，2.sp
        c.created_at = data.created_at # 手机内创建时间
        c.name = data.name
        c.call_count = data.call_count
        c.device_id = data.device_id
        if not need_save:
            return c
        try:
            return c.save()
        except:
            print 'save error'
            return None

    @classmethod
    def create_contacts(cls,contacts):
        contacts_filter = filter(
            None,
            [cls.create_contact(c,need_save=False)  for  c  in  contacts] )
        if not contacts_filter:
            return None
        try:
            cls.objects.insert(
                contacts_filter
            )
            return 'ok'
        except NotUniqueError:
            print 'init UserContact duble key error'
            return None
        except:
            if settings.DEBUG:
                traceback.print_exc()

class UserCallPhone(Document):
    username = StringField(default=str)
    user_id = StringField(required=True)
    owner_phone = StringField(required=True)
    phone=StringField(required=True)
    call_time= DateTimeField()
    created_time = DateTimeField()
    call_duration = IntField(0)
    source =StringField(default=str)
    location=StringField(default=str)
    phone_location = StringField(default=str)
    call_type=StringField(default=str)

    meta = {
        "indexes": [
            'user_id', '-created_time'
        ],
        'index_background': True
    }

    @classmethod
    def create_call(cls,data,need_save=True):
        call = cls()
        call.owner_phone = data.owner_phone
        call.username = data.username
        call.user_id = data.user_id
        call.phone = data.phone
        call.call_time = data.call_time
        call.call_duration = data.call_duration
        call.created_time = datetime.datetime.now()
        call.source = data.source
        call.location=data.location
        call.phone_location=data.phone_location      
        call.call_type=data.call_type
        if not need_save:
            return call
        try:
            return call.save()
        except:
            return None

    @classmethod
    def create_calls(cls,contacts):
        contacts_filter = filter(
        None,
        [cls.create_call(c,need_save=False) for c in contacts])
        if not contacts_filter:
            return None
        try:
            cls.objects.insert(
                contacts_filter,
                write_concern={'continue_on_error': True})
            return 'ok'
        except NotUniqueError:
            print 'init UserCallphone double key error'
            return None
        except:
            if settings.DEBUG:
                traceback.print_exc()
        return None

class UserShortMessage(Document):
    username = StringField(default = str)
    user_id = StringField(required=True)
    #phone=StringField(required=True,unique_with=['user_id', 'username'])
    phone=StringField(required=True)
    owner_phone = StringField(required=True)
    send_time= DateTimeField()
    created_time = DateTimeField()
    source =StringField(default=str)
    location=StringField(default=str)
    phone_location = StringField(default=str)
    sms_type=StringField(default=str)
    meta = {
        "indexes": [
            'user_id', '-created_time'
        ],
        'index_background': True
    }

    @classmethod
    def create_sms(cls,data,need_save = True):
        sms = cls()
        sms.owner_phone = data.owner_phone
        sms.user_id = data.user_id
        sms.username = data.username
        sms.phone = data.phone
        sms.send_time = data.send_time
        sms.created_time = datetime.datetime.now()
        sms.source = data.source
        sms.location=data.location
        sms.phone_location=data.phone_location
        sms.sms_type=data.sms_type
        if not need_save:
            return sms
        try:
            return sms.save()
        except:
            return None

    @classmethod
    def create_smses(cls,contacts):
        smss_filter = filter(
        None,
        [cls.create_sms(c,need_save=False) for c in contacts])
        print smss_filter
        
        if not smss_filter:
            return None
        try:
            cls.objects.insert(
                smss_filter,
                write_concern={'continue_on_error': True})
            return 'ok'
        except NotUniqueError:
            print 'init sms double key error'
            return None
        except:
            if settings.DEBUG:
                traceback.print_exc()
        return None

#上网
class UserNetInfo(Document):
    owner_phone = StringField(required=True)
    user_id = StringField(required=True)
    start_time= DateTimeField()
    sum_flow = StringField(default = str)
    created_time = DateTimeField()
    comm_time = IntField(0)
    net_type = StringField(default = str)
    net_location=StringField(default=str)
    net_source = StringField(default = str)

    @classmethod
    def create_net(cls,data,need_save=True):
        n=cls()
        n.owner_phone = data.owner_phone
        n.user_id = data.user_id
        n.start_time = data.start_time
        n.sum_flow = data.sum_flow
        n.created_time = datetime.datetime.now()
        n.comm_time = data.comm_time
        n.net_type = data.net_type
        n.net_location = data.net_location
        n.net_source = data.net_source
        if not need_save:
            return n
        try:
            return n.save()
        except:
            return None

    @classmethod
    def create_nets(cls,nets):
        n_filter = filter(
        None,
        [cls.create_net(n,need_save=False) for n in nets])
        if not n_filter:
            return None
        try:
            cls.objects.insert(
                n_filter,
                write_concern={'continue_on_error': True})
            return 'ok'
        except:
            if settings.DEBUG:
                traceback.print_exc()
        return None
    
#京东
class jingdong(Document):
    safe_priority = StringField(default = str)
    loginhistory = StringField(default = str)
    address = StringField(default = str)
    bankinfo = StringField(default = str)
    chengzhangzhi=StringField(default = str)
    huiyuanjibie=StringField(default=str)
    jd1_login_name = StringField(name=u'*登录名：',default=str)
    three_month_consume = StringField(name=u'3month_consume',default = str)
    three_month_before_consume = StringField(name=u'3month_before_consume',default = str)
    unknow = StringField(name=u' ',default=str)
    isrealname=StringField(name=u'实名认证',default=str)
    nickname= StringField(name=u'*昵称：',default=str)
    login_pwd=StringField(name=u'登录密码',default=str) 
    sex=StringField(name=u'*性别：',default=str)
    relname=StringField(name=u"*真实姓名：",default=str)
    isvalidphone=StringField(name=u'手机验证',default=str)
    hobbies=StringField(name=u'兴趣爱好：',default=str)
    numvalid=StringField(name=u'数字证书',default=str)
    jd_login_name = StringField(default=str)
    email = StringField(name=u'邮箱：',default=str)
    paypwd=StringField(name=u'支付密码',default=str)
    birthday=StringField(name=u'生日：',default=str)
    validemail = StringField(name=u'邮箱验证',default=str)
    vipchangehistory= StringField(default=str)    
    username=StringField(name=u'用户名：',default=str)
    
#淘宝
class tabao(Document):
    pass
#移动chinaMobile
class yidong(Document):
    base_info =StringField(default=str)
    phone_no = StringField(default= str)
    yue = StringField(default = str)
    recharge = ListField()
    business = StringField(default = str)
    fixed = ListField()
    phonedetail = ListField()
    smsdetail = ListField()
    netdetail = ListField()

    t1 = StringField(name='201605--fixed')
    t2 = StringField(name='201605--phonedetail')
    t3 = StringField(name='201605--netdetail')
    t4 = StringField(name='201605--smsdetail')
    
    t11 = StringField(name='201604--fixed')
    t21 = StringField(name='201604--phonedetail')
    t31 = StringField(name='201604--netdetail')
    t41 = StringField(name='201604--smsdetail')

    t12 = StringField(name='201603--fixed')
    t22 = StringField(name='201603--phonedetail')
    t32 = StringField(name='201603--netdetail')
    t42 = StringField(name='201603--smsdetail')

    t13 = StringField(name='201602--fixed')
    t23 = StringField(name='201602--phonedetail')
    t33 = StringField(name='201602--netdetail')
    t43 = StringField(name='201602--smsdetail')

    t14 = StringField(name='201601--fixed')
    t24 = StringField(name='201601--phonedetail')
    t34 = StringField(name='201601--netdetail')
    t44 = StringField(name='201601--smsdetail')

    t15 = StringField(name='201512--fixed')
    t25 = StringField(name='201512--phonedetail')
    t35 = StringField(name='201512--netdetail')
    t45 = StringField(name='201512--smsdetail')

    t16 = StringField(name='201511--fixed')
    t26 = StringField(name='201511--phonedetail')
    t36 = StringField(name='201511--netdetail')
    t46 = StringField(name='201511--smsdetail')

    t17 = StringField(name='201510--fixed')
    t27 = StringField(name='201510--phonedetail')
    t37 = StringField(name='201510--netdetail')
    t47 = StringField(name='201510--smsdetail')



#联通chinaUnicom
class liantong(Document):
    base_info =StringField(default=str)
    phone_no = StringField(default= str)
    yue = StringField(default = str)
    recharge = StringField(default = str)
    business = StringField(default = str)
    fixed = ListField()
    phonedetail = ListField()
    smsdetail = ListField()
    netdetail = ListField()
#电信
class chinaTelecom(Document):
    base_info =StringField(default=str)
    phone_no = StringField(default= str)
    yue = StringField(default = str)
    recharge = StringField(default = str)
    business = StringField(default = str)
    fixed = ListField()
    phonedetail = ListField()
    smsdetail = ListField()
    netdetail = ListField()

#手机联系人
class phonebook(Document):
    user_id = StringField(default=str)
    name = StringField(default=str)
    phone = StringField(default=str)
    linkmen = StringField(default=str) 
    device_id=StringField(default=str)



class minRule(Document):
    ruleid=StringField(default = str)
    value = StringField(default = str)
    feature_val = StringField(defalt = str) #特征值
    score = FloatField(default = 0)
    name = StringField(default = str)
    source = StringField(default = str)


class DetailRule(Document):
    rule_id = IntField(required=True)
    name = StringField(required=True)
    score = IntField(default=-1)
    rules = ListField(ReferenceField(minRule))

class topResult(Document):
    user_id = StringField(default = str)
    score = FloatField(default = 0)
    rulelist=ListField(ReferenceField(DetailRule))
    value=StringField(default = str)
    name = StringField(default = str)
    created_time = datetime.datetime.now()
