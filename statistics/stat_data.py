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
import json
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
        u'是否实名认证' : u'------',
        u'姓名' : u'unknow',
        u'身份证号' : basedata.idcard_info['idcard'],
        u'性别' : basedata.idcard_info['sex'],
        u'年龄' : basedata.idcard_info['age'],
        u'身份证地址' : basedata.idcard_info['home_location'],
        u'申请人身份证号码是否出现在法院黑名单上' : u'unknow'

    }

'''电商分析'''
def init_online_shop_info(basedata,jd):
    bjd = basedata and basedata.jd or None
    login_his = jd and jd.login_his_map.keys() or []
    login_his.sort()

    def init_jd_info(basedata):
        pass

    def init_tb_info(basedata):
        pass

    jd_basic_info={
        u'会员名':bjd and bjd.jd1_login_name or u'unknow',    
        u'会员等级':bjd and bjd.huiyuanjibie or u'unknow',
        u'是否实名验证':jd and jd.min_rule_map[30001].feature_val or u'unknow',
        u'绑定手机号' : u'unknow',
        u'登陆邮箱' : bjd and bjd.email or u'unknow',
        u'最近登录时间' : len(login_his)>0 and login_his[-1] or u'unknow',
        u'累计使用时间' : u'unknow'
    }
    tb_basic_info = {
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
    jd_consume_info = {
        u'累计消费总额' : jd and jd.min_rule_map[30005].feature_val or u'unknow',
        u'累计消费笔数' : jd and jd.min_rule_map[30006].feature_val or u'unknow',
        u'单笔最高消费' : len(cm_list) and cm_list[-1] or u'unknow',
        u'单笔最低消费' : len(cm_list) and cm_list[0] or u'unknow',
        u'平均每笔消费' : (jd and float(jd.min_rule_map[30005].source) or 0)*1.0/(jd and float(jd.min_rule_map[30006].source) or 1),
        u'累计订单总数' : len(consume_list),
        u'商品总件数' : u'unknow',
        u'返修退换货比率' : u'unknow',
        u'评价总数' : u'unknow',
        u'差评比率' : u'unknow',
    }
    tb_consume_info = {
        u'累计消费总额' : u'unknow',
        u'累计消费笔数' : u'unknow',
        u'单笔最高消费' : u'unknow',
        u'单笔最低消费' : u'unknow',
        u'平均每笔消费' : u'unknow',
        u'累计订单总数' : u'unknow',
        u'商品总件数' : u'unknow',
        u'返修退换货比率' : u'unknow',
        u'评价总数' : u'unknow',
        u'差评比率' : u'unknow',
    }

    jd_addr_info = jd and jd.init_info_mp(basedata) or {}
    jd_addr_detail_list = []
    flag_list=[]
    for k,v in jd_addr_info.items():
        for it in v:
            if it['value'] not in flag_list:
                jd_addr_detail_list.append({
                    u'收货人' : k,
                    u'所在地区' : u'----',
                    u'地址' : it['value'],
                    u'手机' : it['phone'],
                    u'固定电话' : it['tel_phone'] or '---',
                    u'电子邮箱' : it['email'] or '---',
                    u'第一次送货时间' : u'---',
                    u'最后一次送货时间' : u'---',
                    u'订单数' : u'---',
                    u'消费总额' : u'---',
                    u'来源(淘宝/京东)' : u'京东',
                })
                flag_list.append(it['value'])
    tb_addr_detail_list = [{
        u'收货人' : u'unknow',
        u'所在地区' : u'unknow',
        u'地址' : u'unknow',
        u'手机' : u'unknow',
        u'固定电话' : u'unknow',
        u'电子邮箱' : u'unknow',
        u'第一次送货时间' : u'unknow',
        u'最后一次送货时间' : u'unknow',
        u'订单数' : u'unknow',
        u'消费总额' : u'unknow',
        u'来源(淘宝/京东)' : u'淘宝'
    }]

    jd_limit_amount_info = {
        u'白条额度':u'unknow',
        u'白条剩余额度':u'unknow',
        u'白条累计消费':u'unknow',
        u'芝麻信用分数':u'unknow',
        u'花呗额度':u'unknow'
    }
    tb_limit_amount_info = {
        u'白条额度':u'unknow',
        u'白条剩余额度':u'unknow',
        u'白条累计消费':u'unknow',
        u'芝麻信用分数':u'unknow',
        u'花呗额度':u'unknow'
    }
    
    tb_valid_info = {
        u'实名认证是否与美信生活实名认证一致':u'unknow',
    }
    jd_valid_info = {
        u'实名认证是否与美信生活实名认证一致':u'unknow',
    }
    
    jd_addr_info = {
        u'收获人中是否有申请人' : jd and jd.min_rule_map[30007].feature_val or u'unknow',
        u'不同的收货地址个数' : jd and jd.min_rule_map[30008].feature_val or u'unknow',
        u'收件人出现在通讯录中' : jd and jd.min_rule_map[30009].feature_val or u'unknow',
        u'与收件人有短信联系' : jd and jd.min_rule_map[30010].feature_val or u'unknow',
        u'申请用户手机归属地出现在收货地址中': jd and jd.min_rule_map[30012].feature_val or u'unknow',
        u'与收件人有电话联系' : jd and jd.min_rule_map[30011].feature_val or u'unknow'
    }
    tb_addr_info={
        u'收获人中是否有申请人' : u'unknow',
        u'不同的收货地址个数' : u'unknow',
        u'收件人出现在通讯录中' : u'unknow',
        u'与收件人有短信联系' : u'unknow',
        u'申请用户手机归属地出现在收货地址中': u'unknow',
        u'与收件人有电话联系' : u'unknow'
    }
    

    map_info={}
    month_map_info = {}
    stage_map_info = { 1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0 }
    jd_order_info=[]
    ll=[]
    for it in consume_list:
        key=it['time'].date()
        key_str=str(key).split('-')
        kk = key_str[0]+'-'+key_str[1]
        money=it['money']

        if money<=50:
            stage_map_info[1]+=1
        elif money>50 and money<=100:
            stage_map_info[2]+=1
        elif money>100 and money<=200:
            stage_map_info[3]+=1
        elif money>200 and money<=500:
            stage_map_info[4]+=1
        elif money>500 and money<=1000:
            stage_map_info[5]+=1
        elif money>1000 and money<=3000:
            stage_map_info[6]+=1
        elif money>3000 and money<=8000:
            stage_map_info[7]+=1
        elif money>8000:
            stage_map_info[8]+=1

        if kk not in month_map_info:
            month_map_info[kk]=0
        if kk in str(key):
            month_map_info[kk]+=it['money']

        if key not in map_info:
            map_info[key]={'amount':0,'pac_num':0}
        map_info[key]['amount']+=it['money']
        map_info[key]['pac_num']+=1

    for it in consume_list:
        k=it['time'].date()
        if k not in ll:
            jd_order_info.append({
                u'订单日期':str(k),
                u'商品名称':u'---',
                u'商品件数':str(map_info[k]['pac_num']),
                u'总额':str(map_info[k]['amount']),
                u'支付方式': u'---',
                u'收货地址': u'---',
                u'收货人':u'---'
            })
            ll.append(k)
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
    #汇集
    info = {
        u'基本信息' : {
            u'name' : [
                u'会员名',
                u'会员等级',
                u'是否实名验证',
                u'绑定手机号',
                u'登陆邮箱',
                u'最近登录时间',
                u'累计使用时间'
            ],
            u'type' : u'json',
            u'京东':jd_basic_info,
            u'淘宝':tb_basic_info
        },
        u'额度' : {
            #u'name' : [
            #    u'白条额度',
            #    u'芝麻信用分数',
            #    u'花呗额度'
            #],
            u'type' : u'json',
            u'京东' : jd_limit_amount_info,
            u'淘宝' : {},
            #u'淘宝' : tb_limit_amount_info
        },
        u'美信认证' :{
            u'name' : [u'实名认证是否与美信生活实名认证一致'],
            u'type' : u'json',
            u'京东':jd_valid_info,
            u'淘宝':tb_valid_info
        },
        u'消费金额' :{
            u'name' : [
                u'累计消费总额',
                u'累计消费笔数',
                u'单笔最高消费',
                u'单笔最低消费',
                u'平均每笔消费',
                u'累计订单总数',
                u'商品总件数',
                u'返修退换货比率',
                u'评价总数',
                u'差评比率'
            ],
            u'type' : u'json',
            u'京东':jd_consume_info,
            u'淘宝':tb_consume_info
        },
        u'收件人分析': {
            u'type' : u'jsonArray',
            u'京东':jd_addr_detail_list,
            u'淘宝':tb_addr_detail_list
        },
        u'地址':{
            u'type' : u'json',
            u'京东':jd_addr_info,
            u'淘宝':tb_addr_info
        },
        u'图表':{
            u'type' : u'json-json',
            u'京东':{
                u'data1':stage_map_info,
                u'data2':month_map_info,
            },
            u'淘宝':{
                u'data1':{},
                u'data2':{}
            }
        },
        u'订单记录':{
            u'type':u'jsonArray',
            u'京东': jd_order_info,
            u'淘宝': tb_order_info
        }
    }
 
    return info



'''通讯录'''
def init_contact_info(basedata,postloan):

    contact_list = basedata and basedata.contacts or []
    clen=len(contact_list) or 1
    upl=basedata and basedata.user_plocation or ''
    hl=basedata and basedata.home_location or ''
    count=0
    ic=0
    for c in contact_list:
        location=c.phone_location.split('-')
        if location[1] in upl or location[0] in upl:        
            count += 1
        if location[1] in hl or location[0] in hl:
            ic +=1

    same_with_pl_info = {
        u'通讯录中手机号归属地与申请人手机归属地一致个数' : str(count),
        u'通讯录中手机号归属地与申请人手机归属地一致比率' : "%.2f"%(count*1.0/clen),
        u'通讯录中手机号归属地与申请人身份证区域一致个数' : str(ic),
        u'通讯录中手机号归属地与申请人身份证区域一致比率' : "%.2f"%(ic*1.0/clen)
    }

    relative_info = []
    contact_info = []
    relatives_map={}
    relatives_map.update(postloan and postloan.father_mp or {})
    relatives_map.update(postloan and postloan.mather_mp or {})
    relatives_map.update(postloan and postloan.home_mp or {})
    relatives_map.update(postloan and postloan.r_relative_map or {})
    for c in contact_list:
        temp_c={
            u'称呼':c.name,
            u'电话' : c.phone,
            u'归属地' : c.phone_location,
            u'备注' : u'---'
        }
        if c.phone in relatives_map: 
            relative_info.append(temp_c)
        else:
            contact_info.append(temp_c)

    info = {
        u'通讯录':same_with_pl_info,
        u'亲属' : relative_info,
        u'通讯录总览' : contact_info
    }

    return info

'''通话记录'''
def init_sp_record_info(basedata,sp,p):
    
    bas_info=json.loads(basedata.sp and basedata.sp.base_info or '{}')
    data=bas_info and bas_info['data'] or {}
    basic_info={
        u'运营商实名认证' : u'unknow',
        u'运营商实名与自有实名是否一致':u'unknow',
        u'入网时间' : u'unknow',
        u'地址' : data and data['address'] or u'unknow',
        u'网龄' : data and data['netAge'] or u'unknow'
    }

     


    #no_arrearage_info = {
    #    u'长时间关机（连续3天没上网)' : u'unknow',
    #    u'呼叫法院相关号码': u'unknow',
    #    u'申请人号码是否出现在网贷黑名单上':u'unknow',
    #}

    sp_calls = basedata and basedata.sp_calls or []
    call_info=[]
    call_map={}
    month_info={}

    for call in sp_calls:
        if call.phone not in call_map:
            call_map[call.phone]={u'call_in':0,u'call_out':0,u'call_count':0}
        if call.call_type==u'主叫':
            call_map[call.phone][u'call_out'] +=1
        elif call.call_type==u'被叫':
            call_map[call.phone][u'call_in'] +=1
        call_map[call.phone][u'call_count'] += 1
        #按月统计
        key=str(call.call_time.year)+'-'+str(call.call_time.month)
        if key not in month_info:
            month_info[key]={u'call_out':0,
                u'call_in':0,
                u'message':0,
                u'consume':0
            }    
        if key in str(call.call_time):
            month_info[key][u'call_out']+=1
            month_info[key][u'call_in']+=1
            
    for msg in basedata and basedata.sp_sms or []:
        key=str(msg.send_time.year)+'-'+str(msg.send_time.month)
        if key in month_info:
            month_info[key][u'message']+=1


    for call in sp_calls:
        key=call.phone
        call_info.append({
            u'通讯录匹配' : call.username !=u'none' and u'匹配' or u'未匹配',
            u'号码' : key,
            u'通话时间' : str(call.call_duration),
            u'通话次数' : str(call_map[key][u'call_count']),
            u'归属地' : call.phone_location,
            u'被叫次数' : str(call_map[key][u'call_in']),
            u'主叫次数' : str(call_map[key][u'call_out'])
        })
    #net_list=[]
    #for net in basedata and basedata.sp_net or []:
    #    net_list.append(net.start_time)
    #排序
    #net_list.sort()
    #max_inter = 2
    #for i in range(0,len(net_list)-1):
    #    day=(net_list[i+1] - net_list[i]).days
    #    max_inter=max_inter<day and day or max_inter

    no_arrearage_info = {
        #u'长时间关机（连续几天没上网)' : str(max_inter)+'天',
        u'长时间关机（连续3天无数据、无通话、无短信记录':u'unknow',
        u'呼叫法院相关号码': u'unknow',
        u'申请人号码是否出现在网贷黑名单上':u'unknow',
    }    


    contact_info ={
        u'通话记录长度' : sp and sp.min_rule_map[20001].feature_val or u'unknow', 
        u'短信记录长度' : sp and sp.min_rule_map[20002].feature_val or u'unknow',
        u'半年内主叫次数' : sp and sp.min_rule_map[20006].feature_val or u'unknow',
        u'半年内主叫时长' : sp and sp.min_rule_map[20007].feature_val or u'unknow',
        u'半年内被叫次数' : sp and sp.min_rule_map[20008].feature_val or u'unknow',
        u'半年内被叫时长' : sp and sp.min_rule_map[20009].feature_val or u'unknow',
        u'亲属长度' : p and p.min_rule_map[50006] or u'unknow',
        u'亲属在老家的个数' : p and p.min_rule_map[50007] or u'unknow',
        u'亲属通话时长' : p and p.min_rule_map[50008] or u'unknow',
        u'亲属通话次数' : p and p.min_rule_map[50009] or u'unknow'
    }
        

    consume_level_info={
        u'半年内充值金额':sp and sp.min_rule_map[20003].feature_val or u'unknow',
        u'半年内充值次数':sp and sp.min_rule_map[20004].feature_val or u'unknow',
        u'半年内平均充值间隔' : sp and sp.min_rule_map[20005] or u'unknow',
        u'月均消费' : sp and float(sp.min_rule_map[20003].source)/6.0 or u'unknow'
    }


    basic_info_month=[]    
    for k,v in month_info.items():
        basic_info_month.append({
            u'月份' : key,
            u'主叫时间（minutes）':str(v[u'call_out']/60),
            u'被叫时间(minuntes)' :str(v[u'call_in']/60),
            u'短信数量' : str(v[u'message']),
            u'话费消费' : str(v[u'consume']),
        })

    info = {
        u'基本信息1' : basic_info,
        u'基本信息2' : no_arrearage_info,
        u'通话记录' : call_info,
        u'人际交往密切程度' : contact_info,
        u'近期月均消费水平' : consume_level_info,
        u'运营商月消费' : basic_info_month,
    }

    return info

