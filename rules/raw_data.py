# coding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# Create your models here.
import datetime
from mongoengine import (
    StringField, IntField, Document, DateTimeField, BooleanField,
    ObjectIdField,ListField,ListField,ReferenceField,FloatField,NotUniqueError,
)
# from corelib.storage import Storage
import traceback
from django.db import models
# from corelib.utils.strings import underscoreize
from django.conf import settings
# from raven.contrib.django.raven_compat.models import client
 
#用户通讯录
class UserContact(Document):
    username = StringField(default = str)
    owner_id = StringField(default = str)
    order_id = StringField(default = str)
    create_time = DateTimeField()
class UserCallPhone(Document):
    username = StringField(default = str)
    owner_id = StringField(default = str)
    call_time= DateTimeField()
    create_time = DateTimeField()
    call_duration = IntField(0)
    source =StringField(default=str)
    location=StringField(default=str)
    phone_location = StringField(default=str)
    phone=StringField(default=str)
    call_type=StringField(default=str)

    @classmethod
    def create_call(cls,data):
        call = cls()
        call.owner_id = data.owner_id
        call.username = data.username
        call.phone = data.phone
        call.call_time = data.call_time
        call.call_duration = data.call_duration
        call.created_time = datetime.datetime.now()
        call.source = data.source
        call.location=data.location
        call.phone_location=data.phone_location      
        call.call_type=data.call_type
        try:
            return call.save()
        except:
            return None

    @classmethod
    def create_calls(cls,contacts):
        contacts_filter = filter(
        None,
        [cls.create_call(c) for c in contacts])
        if not contacts_filter:
            return None
        #try:
            cls.objects.insert(
                contacts_filter,
                write_concern={'continue_on_error': True})
        #except NotUniqueError:
        #    return None
        #except:
        #    if settings.DEBUG:
        #        traceback.print_exc()
        #    else:
        #        client.captureException()





class UserShortMessage:
    username = StringField(default = str)
    owner_id = StringField(default = str)
    order_id = StringField(default = str)
    create_time =DateTimeField()
    send_time = DateTimeField()
    content = StringField(default = str)
    
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

class minRule(Document):
    ruleid=StringField(default = str)
    value = StringField(default = str)
    score = FloatField(default = 0)
    name = StringField(default = str)
    source = StringField(default = str)
class topResutl(Document):
    user_phone = StringField(default = str)
    score = FloatField(default = 0)
    rulelist=ListField(ReferenceField(minRule))
    value=StringField(default = str)
    name = StringField(default = str)
