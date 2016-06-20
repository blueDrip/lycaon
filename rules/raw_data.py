# coding=utf8
import sys
reload(sys)
# Create your models here.
import datetime
from mongoengine import (
    StringField, IntField, Document, DateTimeField, BooleanField,
    ObjectIdField,ListField,DictField,ReferenceField,FloatField,NotUniqueError,
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
    

#new
class JdData(Document):
    safe_priority = StringField(default = str) 
    growth_value = StringField(default = str)
    sex = StringField(default = str)
    hobbies = StringField()
    consume_list = ListField()
    baitiao = DictField()
    small_credit = DictField()
    login_history = StringField(default = str)
    phone_verifyied = DictField(default = {})
    email_host = StringField(default=str)
    username = StringField(default = str)
    bankinfo = ListField(default = [])
    login_name_varifyied = DictField(default = {})
    indentify_verified = DictField(defalut = {})
    address = ListField(default = [])
    license_verified = DictField(default = {})
    nickname = StringField(default = str)
    jd_login_name = StringField(default = str,required=True)
    email_verified = DictField(default = {})
    real_name = StringField(default=str)
    user_level = StringField(default = str)
    pay_passwd_verified = DictField(default = {})
    login_name = StringField(default = str)
    
#淘宝
class TaoBao(Document):
    taobao_name = StringField(default=str) #淘宝登录名
    createTime = DateTimeField(default=str) #创建时间
    huabeiCanUseMoney = FloatField(default=0) #花呗可用额度
    creditLevel = StringField(default=str) #//淘宝信用等级
    tianMaoAccountName = StringField(default=str) #天猫用户名
    tianMaoLevel = StringField(default = str) #天猫等级
    taobaoFastRefundMoney = IntField(default=0) #淘宝极速退款额度
    buyerCreditPoint = StringField(default=str) #买家信用评分
    aliPaymFund = StringField(default=str)      #余额宝金额
    tianMaoPoints = StringField(default=str)    #天猫积分
    taobaoLevel = StringField(default=str)      #淘宝等级
    aliPaymFundProfit = StringField(default='0') #余额宝总收益
    aliPayRemainingAmount = StringField(default='0') #支付宝余额
    huabeiTotalAmount = FloatField(default=0) #花呗总额度
    growthValue = StringField(default='0') #淘宝成长值
    tianmaoExperience = StringField(default='0') #天猫经验值
    username = StringField(default=str) #用户名
    pwdProtectedQuestion = StringField(default=str) #未设置密保
    bindMobile = StringField(default=str) #绑定手机号
    loginPasswdVerify = StringField(default=str) #登录密码验证开启
    identityVerified = StringField(default = str) #实名认证是否完成
    loginEmail = StringField(default=str) #登录邮箱
    mobileVerified = StringField(default=str) #是否绑定手机号
    safeLevel = StringField(default=str) 
    addrs = ListField(default=[])
    orderList = ListField(default=[])

#移动
class chinaMobile(Document):

    currRemainingAmount = DictField()
    phonedetail = DictField()
    personalInfo = DictField()
    openBusiness = DictField()
    currPoint = DictField()
    smsdetail = DictField()
    phone_no = StringField()
    businessOrder = DictField()
    netdetail = DictField()
    fixed = DictField()
    createTime = StringField()
    recharge = DictField()


#联通chinaUnicom
class chinaUnicom(Document):
    base_info = DictField()
    phone_no = DictField()
    yue_jifen = DictField
    rechargedetail = DictField()
    phonedetail = DictField()
    personalInfo = DictField()
    smsdetail = DictField()
    netdetail = DictField()
    others = DictField()
    createTime = StringField()
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
    linkmen = DictField(default=str) 
    device_id=StringField(default=str)


#招商信用卡
class cmbcc(Document):
    detailBill = ListField()
    username = StringField()
    canBorrowCash = StringField()
    repaymentInfo =ListField()
    billAddr = ListField()
    simpleBill = ListField()
    canUserAmount = StringField()
    totalAmount = StringField()

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
    created_time = DateTimeField()
    user_type = StringField(default = '正常用户') #黑名单用户
