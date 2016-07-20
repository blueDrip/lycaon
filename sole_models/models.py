# coding=utf8
import sys
reload(sys)
# Create your models here.
import datetime
from mongoengine import (
    StringField, IntField, Document, DateTimeField, BooleanField,
    ObjectIdField,ListField,DictField,ReferenceField,FloatField,NotUniqueError,
    EmbeddedDocument,EmbeddedDocumentField
)
import traceback
from django.db import models
from django.conf import settings
from rules.raw_data import UserCallPhone,chinaUnicom,chinaMobile,chinaTelecom
#用户通讯录


#移动
class chinaMobile_desplay(Document):
#
    currRemainingAmount = DictField()
    phonedetail = DictField()
    personalInfo = DictField()
    openBusiness = DictField()
    smsdetail = DictField()
    phone_no = StringField()
    netdetail = DictField()
    createTime = StringField()
    recharge = DictField()
    historyBillInfo = DictField()


    

#联通chinaUnicom
class chinaUnicom_desplay(Document):
    rechargedetail = DictField() #paymentRecord
    phonedetail = DictField()    # calldetail
    smsdetail = DictField()      # smsdetail
    netdetail = DictField()      # netdetail
    createTime = StringField()   # createTime
    historyBillInfo = DictField() #histtoryBillInfo
    userinfo = DictField()
    phoneInfo = DictField()
    phone_no = StringField()

    #pchinaUnicom = EmbeddedDocumentField(chinaUnicom)
    

#电信
#class chinaTelecom(Document):
#    base_info =StringField(default=str)
#    phone_no = StringField(default= str)
#    yue = StringField(default = str)
    #recharge = StringField(default = str)
#    business = StringField(default = str)
#    fixed = ListField()
    #phoinedetail = ListField()
    #smsdetail = ListField()
    #netdetail = ListField()


#    phone_no = DictField()
#    rechargedetail = DictField()
#    phonedetail = DictField()
#    smsdetail = DictField()
#    netdetail = DictField()
#    createTime = StringField()
#    historyBillInfo = DictField()

#    address = StringField(default = '') #地址
#    phone_using_time = StringField() #手机号创办时间
#    netage = StringField(default='')
#    userphone = StringField() #手机号
#    real_name = StringField() #姓名

