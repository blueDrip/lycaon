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
from rules.ruleset.Tbao import Tbao
from rules.ruleset.PersonInfo import PersonInfo
from rules.ruleset.Sp import Sp
from rules.ruleset.postloan import PostLoanNewRule
from rules.ruleset.creditCard import creditCard
from rules.models import BaseRule
from rules.base import BaseData
from rules.ext_api import EXT_API
from rules.util.utils import get_tb_info
from api.models import Profile,Idcardauthlogdata,Yunyinglogdata,Dianshanglogdata,BankAccount,Busers
from rules.raw_data import phonebook,cmbcc
from rules.orm import tb_orm,china_mobile_orm,jd_orm,china_unicom_orm,phonebook_orm
from rules.util.sms_email import MyEmail
from statistics.models import RulesInfo
from statistics.stat_data import init_valid_name_info,init_online_shop_info,init_contact_info,init_sp_record_info
cal_logger = logging.getLogger('django.cal')
cal_logger.setLevel(logging.INFO)

base_logger = logging.getLogger('django.rules')
base_logger.setLevel(logging.INFO)

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

    cal_logger.info(str_token)
    token_list = [ it for it in str_token.split(';') ]
    #token
    user_id_token = token_list[0]
    idcard_token = token_list[1]
    user_phone_token = token_list[2]
    sp_phone_no_token = token_list[3]
    phone_book_token = token_list[4]
    taobao_name_token = token_list[5]
    jd_name_token = token_list[6]
    
    '''当前授权的项数'''
    authorize_item_count =  idcard_token != 'None' and 1 or 0         #授权身份认证
    authorize_item_count += sp_phone_no_token != 'None' and 1 or 0   #授权运营商
    authorize_item_count += phone_book_token != 'None' and 1 or 0    #授权通讯录
    authorize_item_count += taobao_name_token != 'None' and 1 or 0   #授权淘宝
    authorize_item_count += jd_name_token != 'None' and 1 or 0       #授权京东

    cal_logger.info('【authorize_item_count】 '+str(authorize_item_count))

    '''user,sp,jd,phonecontact,cb'''
    idcard,sp,jd,tb,ucl,cb=None,None,None,None,None,None
    userinfo = Profile.objects.using('users').filter(user_id = binascii.a2b_hex(user_id_token.replace('-',''))).first()
    user_id=user_id_token.replace('-','').upper()
    try:
        sp = Yunyinglogdata.objects.filter( uuid = sp_phone_no_token).first()
        sp_phoneno = sp and sp.phoneno or str(None)

        sp_mobile=china_mobile_orm({ "phone_no" : sp_phoneno })
        sp_unicom=china_unicom_orm({ "phone_no" : sp_phoneno })
        sp = sp_mobile or sp_unicom
    except:
        sp=None
        base_logger.error(get_tb_info())
        base_logger.error("【 error 】" + " USER_ID:  "+user_id)

    try:
        online_shop = Dianshanglogdata.objects.filter(uuid = jd_name_token).first()
        jd_loginname = online_shop and online_shop.loginname or str(None)
        jd = jd_orm({"jd_login_name" : jd_loginname})
    except:
        jd=None
        base_logger.error(get_tb_info())
        base_logger.error("【 error 】" + "  USER_ID: "+user_id)
    try:
        online_shop = Dianshanglogdata.objects.filter(uuid = taobao_name_token).first()
        tb_loginname = online_shop and online_shop.loginname or str(None)
        tb=tb_orm(cnd={"taobao_name" : tb_loginname})
    except:
        tb=None
        base_logger.error(get_tb_info())
        base_logger.error("【 error 】" + "  USER_ID: "+user_id)
    try:
        ucl = phonebook_orm({ "token" : phone_book_token})
    except:
        ucl=None
        base_logger.error(get_tb_info())
        base_logger.error("【 error 】" + "  USER_ID: "+user_id)

    try:
        #cb = cmbcc.objects.filter(id=u'573ae5201d41c83f39423b9d').first()
        #bank_login_name = BankAccount.objects.filter(token='').first()
        cb=None
    except:
        cb=None
        base_logger.error(get_tb_info())
        base_logger.error("【 error 】" + "  USER_ID: "+user_id)
    return {
        'user':userinfo,
        'user_id':user_id,
        'user_phone':user_phone_token,
        'idcard':idcard_token,
        'jd' : jd,
        'tb' : tb,
        'sp' : sp,
        'ucl': ucl,
        'cb' : cb,
        'token' : str_token,
        'authorize_item_count':authorize_item_count
    }
#逻辑控制,规定何时算分
def cal_by_message(msg):
    rmap=get_token(msg)
    user_id = rmap['user_id']

    id_card = rmap['idcard']

    is_author = rmap['idcard'] and rmap['sp'] and rmap['ucl'] and (rmap['jd'] or rmap['tb'])
    #如果当前授权不全,等待
    if not is_author:
       cal_logger.info('【 抓取未完成 】')
       return None
    top_rs = topResult.objects.filter(user_id = user_id).order_by('-created_time').first()
    if top_rs:
        auitem = top_rs.authorize_item_count
        score = int(top_rs.score)
        old_token = top_rs.token
        #是否重新授权
        new_token_list = [ it for it in msg.replace('None','').split(';') if not str(it).isdigit() ]
        is_agrain_author = not len([ it for it in new_token_list if it in old_token ])>2

        #只要每次授权的比上次的多，就重新算分
        if not is_agrain_author and auitem == rmap['authorize_item_count']:
            cal_logger.info('【 当前分数 】: '+str(score))
            return score

    #重新授权或授权项变多
    return cal(minfo=rmap)


def cal(minfo = {
        'user':None,
        'user_id':str(None),
        'user_phone':str(None),
        'idcard':None,
        'jd':None,
        'tb':None,
        'sp':None,
        'ucl':None,
        'cb':None,
        'token':'None;None;None;None;None;None;None;None',
        'authorize_item_count':0 }
    ):

    rule_map={'personinfo':PersonInfo,
        'jd' : JD,
        'tb' :Tbao,
        'sp' : Sp,
        'cb' : creditCard,
        'postloan' : PostLoanNewRule,
    }
    name_list={'personinfo':u'个人信息',
        'jd':u'京东',
        'tb':u'淘宝',
        'sp':u'运营商',
        'cb':u'招商信用卡',
        'postloan':u'贷后',
    }
    weight_map={
        'personinfo':0.15,
        'jd':0.15,
        'tb':0.15,
        'sp':0.2,
        'postloan':0.3,
        'cb':0.05,
    }

    '''判断是否为黑名单用户'''
    user_type = u'正常用户'
    if is_apix_basic():
        user_type = u'黑名单'

    ext_api = EXT_API()
    b=BaseRule()
    bd=BaseData(map_info=minfo,ext=ext_api)
    user_id=minfo['user_id'].upper()

    top_rule = topResult()
    top_rule.authorize_item_count = minfo['authorize_item_count'] #记录当前授权的项目
    top_rule.token = minfo['token'] #记录此次的token值

    user_id=minfo['user_id'].upper()
    cal_logger.info(u'【 start calculate score 】 ' + str(user_id))
    #规则计算
    i=1
    for k,rule in rule_map.items():
        detail_rule = DetailRule()
        b=None
        try:
            b=rule(bd)
            #判断是否本人申请
            b.base_line(bd)
            #加载规则
            b.load_rule_data(bd)
            for rd,min_rule in b.min_rule_map.items():
                min_rule.ruleid = str(rd)
                min_rule.value = min_rule.value.replace('\t','<br/>')
                min_rule.save()
                detail_rule.rules.append(min_rule)
            detail_rule.name = name_list[k]
            detail_rule.rule_id = i
            detail_rule.score = int(b.get_score())*10
            detail_rule.save()
        except:
            detail_rule.name = name_list[k]
            detail_rule.rule_id = i
            detail_rule.score = 0
            detail_rule.save()
            base_logger.error(get_tb_info())
            base_logger.error("【 " + k +"  error 】" + 'USER_ID:'+user_id)

        top_rule.rulelist.append(detail_rule)
        top_rule.score+=detail_rule.score*weight_map[k]
        cal_logger.info( name_list[k] +'\t'+str(detail_rule.score))
        i+=1

    top_rule.name = u'credit_score'
    top_rule.user_type = user_type
    top_rule.user_id = user_id
    top_rule.created_time = datetime.now()
    top_rule.save()
    user=minfo['user']
    if user:
        user.trust_score=top_rule.score
        user.save()
    cal_logger.info(u'  【计算完成】 ' + str(top_rule.score))

    #try:
    rule_detail = RulesInfo()
    rule_detail.valid_name_info = init_valid_name_info(bd)
    rule_detail.online_shop_info = init_online_shop_info(bd)
    rule_detail.contact_info = init_contact_info(bd)
    rule_detail.sp_info = init_sp_record_info(bd)
    rule_detail.credit_info = {}
    rule_detail.created_at = datetime.now()
    rule_detail.user_id = user_id
    rule_detail.save()
    print 'stat is finished'   
    #except:
        #print '【详情保存完成】'
    return top_rule.score
