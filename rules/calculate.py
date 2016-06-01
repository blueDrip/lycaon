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
from rules.raw_data import JdData,liantong,yidong
from rules.raw_data import phonebook,cmbcc
from rules.util.sms_email import MyEmail
from statistics.models import RulusDetailInfo
from statistics.stat_data import init_valid_name_info,init_online_shop_info,init_contact_info,init_sp_record_info
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
    e_commerce = Dianshanglogdata.objects.using('django').filter( 
        uuid = str(token_list[3])
    ).first()
    e_commerce_loginname = e_commerce and e_commerce.loginname or str(None)

    bank_login_name = BankAccount.objects.using('django').filter(token='').first()

    '''user,sp,jd,phonecontact,cb'''
    userinfo = Profile.objects.filter(user_id = binascii.a2b_hex(token_list[0].replace('-',''))).first()
    idcard = Idcardauthlogdata.objects.using('django').filter( uuid=str(token_list[1] )).first()
    sp=yidong.objects.filter(phone_no = sp_phoneno).first()
    jd=JdData.objects.filter(jd_login_name = e_commerce_loginname).first()
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

    rule_map={'personinfo':PersonInfo,
        'jd' : JD,
        'sp' : Sp,
        'cb' : creditCard,
        'postloan' : PostLoanNewRule,
    }
    name_list={'personinfo':u'个人信息',
        'jd':u'京东',
        'sp':u'运营商',
        'cb':u'招商信用卡',
        'postloan':u'贷后',
    }
    weight_map={
        'personinfo':0.2,
        'jd':0.3,
        'sp':0.2,
        'postloan':0.2,
        'cb':0.1,
    }

    user_type = u'正常用户'
    if is_apix_basic():
        user_type = u'黑名单'
    ext_api = EXT_API()
    b=BaseRule()
    bd=BaseData(map_info=minfo,ext=ext_api)
    top_rule = topResult()

    user_id=minfo['user_id']
    rules_detail_map={}    

    cal_logger.info(u'【start calculate score】　' + str(user_id))
    #规则计算
    score,i=0,1
    for k,rule in rule_map.items():
        cal_logger.info( name_list[k] +'\t'+str(user_id)+'\t'+ str(datetime.now()) )
        detail_rule = DetailRule()
        b=rule(bd)
        for rd,min_rule in b.min_rule_map.items():
            min_rule.ruleid = str(rd)
            min_rule.value = min_rule.value.replace('\t','<br/>')
            min_rule.save()
            detail_rule.rules.append(min_rule)
        detail_rule.name = name_list[k]
        detail_rule.rule_id = i
        detail_rule.score = int(b.get_score())*10
        detail_rule.save()
        top_rule.rulelist.append(detail_rule)
        top_rule.score+=detail_rule.score*weight_map[k]
        cal_logger.info( name_list[k] + '\t'+ str(user_id)+'\t'+str(datetime.now())+'\t'+str(detail_rule.score))
        #加载模型
        rules_detail_map[k]=b
        i+=1
    top_rule.name = u'credit_score'
    top_rule.user_type = user_type
    top_rule.user_id = minfo['user_id']
    top_rule.save()
    cal_logger.info(u'【计算完成】\t' + str(user_id)+'\t'+str(datetime.now())+'\t'+str(top_rule.score))
    print '【successful!】'

    #try:
    rule_detail = RulusDetailInfo()
    rule_detail.valid_name_info = init_valid_name_info(bd)
    rule_detail.online_shop_info = init_online_shop_info(bd,rules_detail_map['jd'])
    rule_detail.contact_info = init_contact_info(bd,rules_detail_map['postloan'])
    rule_detail.sp_info = init_sp_record_info(bd, rules_detail_map['sp'],rules_detail_map['postloan'])
    rule_detail.credit_info = {}
    rule_detail.created_at = datetime.now()
    rule_detail.user_id = user_id
    rule_detail.save()   
    #except:
        #print '【详情保存完成】'
    return top_rule.score
