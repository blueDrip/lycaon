# coding=utf8
import sys
import os
import django
#sys.setdefaultencoding('utf8')
if __name__ == '__main__':
    local_dir = sys.argv[1]
    sys.path.append(local_dir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lycaon.settings'
    django.setup()
from django.conf import settings
from django.db.models import Q,Sum,F
from rules.models import BaseRule

from mongoengine import (
     StringField, ListField, IntField, Document, EmbeddedDocumentField, FloatField,
     DateTimeField, EmbeddedDocument
)
import logging
import StringIO
logger = logging.getLogger('django.rules')
logger.setLevel(logging.INFO)
import time
from datetime import datetime, date, timedelta

def get_time_now(hours=0,minutes=0,seconds=0):
    today=time.localtime();
    year=today.tm_year;
    month=today.tm_mon;
    day=today.tm_mday;
    return datetime(year,month,day,hours,minutes,seconds)

#set time
def get_start_time(dist=1):
    return get_time_now()-timedelta(days=dist)
def get_stop_time(dist=1):
    return get_time_now(23,59,59)-timedelta(days=dist)

'''实名验证'''
def init_valid_name_info(basedata):
    return {
        u'是否实名认证' : u'unknow',
        u'姓名' : u'unknow',
        u'身份证号' : basedata.idcard_info['idcard'],
        u'性别' : basedata.idcard_info['sex'],
        u'年龄' : basedata.idcard_info['age'],
        u'身份证地址' : basedata.idcard_info['home_location'],
        u'申请人身份证号码是否出现在法院黑名单上' : u'unknow'

    }
'''电商分析'''
def init_online_shop_info(basedata,jd):

    bjd = basedata.jd
    login_his = jd.login_his_map.keys()
    login_his.sort()

    jd_basic_info={
        u'会员名':bjd and bjd.jd1_login_name or u'unknow',    
        u'会员等级':bjd and bjd.huiyuanjibie,
        u'是否实名验证':jd and jd[30001].feature_val or u'unknow',
        u'绑定手机号' : u'unknow',
        u'登陆邮箱' : bjd and bjd.email or u'unknow',
        u'最近登录时间' : len(login_his)>0 and login_his[-1] or u'unknow',
        u'累计使用时间' : u'unknow'
    }
    tb_basic_info ={
        u'会员名' : u'unknow',
        u'会员等级' : u'unknow',
        u'是否实名验证': u'unknow',
        u'绑定手机号' : u'unknow',
        u'登陆邮箱' :  u'unknow',
        u'最近登录时间' : u'unknow',
        u'累计使用时间' : u'unknow'
    
    }


    consume_list = jd and jd.consume_after_list or []
    consume_list.extend(jd and jd.consume_before_3mon_list or [])
    cm_list = [ it['money'] for it in consume_list ]
    cm_list.sort()
    jd_consume_info={
        u'累计消费总额' : jd and jd[30005].feature_val or u'unknow',
        u'累计消费笔数' : jd and jd[30006].feature_val or u'unknow',
        u'商品总件数' : len(consume_list),
        u'单笔最高消费' : len(cm_list) and cm_list[-1] or u'unknow',
        u'单笔最低消费' : len(cm_list) and cm_list[0] or u'unknow',
        u'平均每笔消费' : (jd and jd[30005].feature_val or 0)*1.0/(jd and jd[30006].feature_val or 1),
        u'返修退换货比率' : u'unknow',
        u'评价总数' : u'unknow',
        u'差评比率' : u'unknow',
    } 
    tb_consume_info={
        u'累计消费总额' : u'unknow',
        u'累计消费笔数' : u'unknow',
        u'商品总件数' : u'unknow',
        u'单笔最高消费' : u'unknow',
        u'单笔最低消费' : u'unknow',
        u'平均每笔消费' : u'unknow',
        u'返修退换货比率' : u'unknow',
        u'评价总数' : u'unknow',
        u'差评比率' : u'unknow',
    }

    jd_addr_info = jd.address_info_map
    tb_addr_info = {
        u'地址':u'unknow',
        u'接受订单数':u'unknow',
        u'第一次送货时间':u'unknow',
        u'最后一次送货时间':u'unknow',
        u'消费总额':u'unknow',
        u'收货人姓名':u'unknow',
        u'收货人手机号' : u'unknow',
        u'来源' : u'unknow'    
    }

    jd_limit_amount_info={
        u'京东白条额度' : u'unknow',
        u'芝麻信用分数' : u'unknow',
        u'花呗额度' : u'unknow'
    }
    tb_limit_amount_info={
        u'淘宝额度' : u'unknow',
        u'芝麻信用分数' : u'unknow',
        u'花呗额度' : u'unknow'
    }
    
    tb_valid_info = {
        u'淘宝实名认证是否与美信生活实名认证一致':u'unknow',
    }
    jd_valid_info = {
        u'京东实名认证是否与美信生活实名认证一致':u'unknow',
    }
    
    jd_addr_info = {
        u'收获人中是否有申请人' : jd and jd['30007'].feature_val or u'unknow',
        u'不同的收货地址个数' : jd and jd['30008'].feature_val or u'unknow',
        u'收件人出现在通讯录中' : jd and jd['30009'].feature_val or u'unknow',
        u'与收件人有短信联系' : jd and jd[30010].feature_val or u'unknow',
        u'申请用户手机归属地出现在收货地址中': jd and jd[30012].feature_val or u'unknow',
        u'与收件人有电话联系' : jd and jd[30011].feature_val or u'unknow'
    }
    tb_addr_info={
        u'收获人中是否有申请人' : u'unknow',
        u'不同的收货地址个数' : u'unknow',
        u'收件人出现在通讯录中' : u'unknow',
        u'与收件人有短信联系' : u'unknow',
        u'申请用户手机归属地出现在收货地址中': u'unknow',
        u'与收件人有电话联系' : u'unknow'
    }
    
    jd_order_info={
        u'订单记录':u'unknow',
        u'订单日期':u'unknow',
        u'商品名称':u'unknow',
        u'商品件数':u'unknow',
        u'总额':u'unknow',
        u'支付方式': u'unknow',
        u'收货地址': u'unknow',
        u'收货人':u'unknow'
    }

    tb_order_info={
        u'订单记录':u'unknow',
        u'订单日期':u'unknow',
        u'商品名称':u'unknow',
        u'商品件数':u'unknow',
        u'总额':u'unknow',
        u'支付方式': u'unknow',
        u'收货地址': u'unknow',
        u'收货人':u'unknow'
    }

    pass
'''通讯录'''
def init_contact_info(basedata):
    pass
'''通话记录'''
def init_credit_info(basedata):
    pass







