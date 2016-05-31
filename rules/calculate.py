#!/usr/bin/env python
# encoding: utf-8

import traceback
import socket
import time
import urllib
import datetime
import requests
import binascii
import logging
import json
from datetime import datetime
from rules.raw_data import topResult,DetailRule
from rules.ruleset.JD import JD
from rules.ruleset.PersonInfo import PersonInfo
from rules.ruleset.Sp import Sp
from rules.ruleset.postloan import PostLoanNewRule
from rules.ruleset.creditCard import creditCard
from rules.models import BaseRule
from rules.base import BaseData
from rules.ext_api import EXT_API
from api.models import Profile,Idcardauthlogdata,Yunyinglogdata,Dianshanglogdata,BankAccount
from rules.raw_data import jingdong,liantong,yidong
from rules.raw_data import phonebook,cmbcc
from rules.util.sms_email import MyEmail
cal_logger = logging.getLogger('django.cal')
cal_logger.setLevel(logging.INFO)

def is_apix_basic(query_map={}):
    api_key = 'a8bbd3a565b04acf600e6b053beffea2'
    url = "http://e.apix.cn/apixcredit/blacklist/dishonest"
    querystring = {
        "type":'person',
        "name":'姜俊智',
        "cardno":'440882197508218433',
        "phoneNo":'',
        "email":None
    }
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'apix-key': api_key
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    rs = json.loads(response.text)
    if rs['code'] == 0:
        return True
    return False

def get_token(str_token):

    token_list = [ it for it in str_token.split(';') ]
    sp_phoneno = Yunyinglogdata.objects.using('django').filter( uuid = str(token_list[2])).first().phoneno
    e_commerce_loginname = Dianshanglogdata.objects.using('django').filter( 
        uuid = str(token_list[3])
    ).first().loginname
    bank_login_name = BankAccount.objects.using('django').filter(token='').first()

    '''user,sp,jd,phonecontact,cb'''
    userinfo = Profile.objects.filter(user_id = binascii.a2b_hex(token_list[0].replace('-',''))).first()
    idcard = Idcardauthlogdata.objects.using('django').filter( uuid=str(token_list[1] )).first()
    sp=yidong.objects.filter(phone_no = sp_phoneno).first()
    jd=jingdong.objects.filter(jd_login_name = e_commerce_loginname).first()
    ucl = phonebook.objects.filter(user_id = u'111').first()
    cb = cmbcc.objects.filter(id=u'573ae5201d41c83f39423b9d').first()

    return {
        'user':userinfo,
        'user_id':token_list[0].replace('-',''),
        'idcard':idcard,
        'jd' : jd,
        'tb' : None,
        'sp' : sp,
        'ucl': ucl,
        'cb' : cb
    }

def cal_by_message(msg):
    rmap=get_token(msg)
    s=cal(minfo=rmap)
    user=rmap['user']
    if user:
        user.trust_score=s
        user.save()
        print '【save successful】'

def cal(minfo = {
        'user':None,
        'user_id':str(None),
        'idcard':None,
        'jd':None,
        'tb':None,
        'sp':None,
        'ucl':None,
        'cb':None}
    ):

    user_id=minfo['user_id']
    cal_logger.info(u'【start calculate score】　' + str(user_id))    

    user_type = u'正常用户'
    if is_apix_basic():
        user_type = u'黑名单'

    ext_api = EXT_API()
    b=BaseRule()
    bd=BaseData(map_info=minfo,ext=ext_api)
    b=JD(bd)
    tp_rs = topResult()
    cal_logger.info(u'【个人信息】开始计算\t'+str(user_id)+'\t'+ str(datetime.now()))
    dl=[]
    Dr_p=DetailRule()
    b=PersonInfo(bd)
    for k,v in b.min_rule_map.items():
        v.ruleid = str(k)
        v.value = v.value.replace('\t','<br/>')
        v.save()
        dl.append(v)
    Dr_p.name=u'个人信息'
    Dr_p.rule_id=1
    Dr_p.score=int(b.get_score())*10
    Dr_p.rules=dl
    Dr_p.save()
    cal_logger.info(u'【个人信息】计算完成\t'+str(user_id)+'\t'+str(datetime.now())+'\t'+str(Dr_p.score))
    cal_logger.info(u'【京东】开始计算\t'+str(user_id)+'\t'+str(datetime.now()))
    Dr_jd=DetailRule()
    dl=[]
    b = JD(bd)
    for k,v in b.min_rule_map.items():
        v.ruleid = str(k)
        v.value = v.value.replace('\t','<br/>')
        v.save()
        dl.append(v)
    Dr_jd.name=u'京东'
    Dr_jd.score=int(b.get_score())*10
    Dr_jd.rules=dl
    Dr_jd.rule_id=2
    Dr_jd.save()
    cal_logger.info(u'【京东】计算完成\t' + str(user_id)+'\t'+str(datetime.now())+'\t'+str(Dr_jd.score))
    cal_logger.info(u'【运营商】开始计算\t' + str(user_id)+'\t'+str(datetime.now()))
    dl=[]
    b=Sp(bd)
    Dr_sp=DetailRule()
    for k,v in b.min_rule_map.items():
        v.ruleid = str(k)
        v.value = v.value.replace('\t','<br/>')
        v.save()
        dl.append(v)
    Dr_sp.name=u'运营商'
    Dr_sp.rule_id=3
    Dr_sp.score=int(b.get_score())*10
    Dr_sp.rules=dl
    Dr_sp.save()
    cal_logger.info(u'【运营商】计算结束\t'+str(user_id)+'\t'+str(datetime.now())+'\t'+str(Dr_sp.score))
    cal_logger.info(u'【贷后】开始计算\t'+str(user_id)+'\t'+str(datetime.now()))
    b=PostLoanNewRule(bd)
    Dr_post=DetailRule()
    dl=[]
    for k,v in b.min_rule_map.items():
        v.ruleid=str(k)        
        v.value = v.value.replace('\t','<br/>')
        v.save()
        dl.append(v)
    Dr_post.name=u'贷后'
    Dr_post.rule_id=4
    Dr_post.score=int(b.get_score())*10
    Dr_post.rules=dl
    Dr_post.save()
    cal_logger.info(u'【贷后】计算结束\t'+str(user_id)+'\t'+str(datetime.now())+'\t'+str(Dr_sp.score))
    cal_logger.info(u'【信用卡】开始计算\t'+str(user_id)+'\t'+str(datetime.now()))
    b = creditCard(bd)
    Dr_credit = DetailRule()
    dl = []
    for k,v in b.min_rule_map.items():
        v.ruleid=str(k)
        v.value = v.value.replace('\t','<br/>')
        v.save()
        dl.append(v)
    Dr_credit.name = u'招商银行信用卡'    
    Dr_credit.rule_id=5
    Dr_credit.score=int(b.get_score())*10
    Dr_credit.rules=dl
    Dr_credit.save()
    cal_logger.info(u'【信用卡】计算完成\t'+str(user_id)+'\t'+str(datetime.now())+'\t'+str(Dr_credit.score))
    print 'finish'

    tp_rs.name = u'credit_score'
    tp_rs.score=(Dr_p.score*0.2+Dr_jd.score*0.2+Dr_sp.score*0.3+Dr_post.score*0.2+Dr_credit.score*0.1)
    print Dr_p.score,Dr_jd.score,Dr_sp.score,Dr_post.score,Dr_credit.score
    print '得分',tp_rs.score
    print user_type
    tp_rs.rulelist=[Dr_p,Dr_jd,Dr_sp,Dr_credit,Dr_post]
    tp_rs.user_type = user_type
    tp_rs.user_id = minfo['user_id']
    tp_rs.save()
    cal_logger.info(u'【计算完成】\t' + str(user_id)+'\t'+str(datetime.now())+'\t'+str(tp_rs.score))
    print '【successful!】'
    return tp_rs.score

