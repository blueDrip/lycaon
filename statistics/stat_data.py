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
        u'is_valid_name' : u'unknown',#是否实名认证
        u'name' : u'unknown',#姓名
        u'idcard' : basedata.idcard_info['idcard'],#idcardno
        u'sex' : basedata.idcard_info['sex'],#性别
        u'age' : basedata.idcard_info['age'],#年龄
        u'idcard_location' : basedata.idcard_info['home_location'],#身份证所在地
        u'in_law_black' : u'unknown' #申请人身份证号码是否出现在法院黑名单上
    }

'''电商分析'''
def init_online_shop_info(basedata,jd):
    bjd = basedata and basedata.jd or None
    login_his = jd and jd.login_his_map.keys() or []
    login_his.sort()
    jd_basic_info={
        u'login_name':bjd and bjd.jd_login_name or u'unknown',#会员名    
        u'grade':bjd and bjd.user_level or u'unknown',#会员等级
        u'is_pass_valid':jd and jd.min_rule_map[30001].feature_val or u'unknown',#是否通过姓名验证
        u'binding_phone' : u'unknown',#绑定手机号
        u'login_email' : bjd and bjd.email_host.replace('\r\n','') or u'unknown',#登陆邮箱
        u'last_login_date' : len(login_his)>0 and login_his[-1] or u'unknown',#最后一次登陆时间
        u'total_time':u'unknown' #使用时间
    }
    tb_basic_info = {
        u'login_name' : u'unknown',#会员名    
        u'grade' : u'unknown',#会员等级
        u'is_pass_valid' : u'unknown',#是否通过姓名验证
        u'binding_phone' : 'unknown',#绑定手机号
        u'login_email' : u'unknown',#登陆邮箱
        u'last_login_date' : u'unknown',#最后一次登陆时
        u'total_time':u'unknown'
    }

    consume_list = jd and jd.consume_list or []
    cm_list = [ it['money'] for it in consume_list ]
    cm_list.sort()
    jd_consume_info = {
        u'total_amount' : jd and jd.min_rule_map[30005].feature_val or u'unknown',#累计消费总额
        u'total_consume_orders' : jd and jd.min_rule_map[30006].feature_val or u'unknown',#累计消费笔数
        u'max_money' : len(cm_list) and cm_list[-1] or u'unknown',#单笔最高消费
        u'min_money' : len(cm_list) and cm_list[0] or u'unknown',#单笔最低消费
        u'avg_money' : (jd and float(jd.min_rule_map[30005].source) or 0)*1.0/(jd and float(jd.min_rule_map[30006].source) or 1),#平均每笔消费
        u'total_orders' : len(consume_list),#累计订单总数
        u'goods_nums' : u'unknown',#商品总件数
        u'back_goods_radio' : u'unknown',#返修退换货比率
        u'judge_times' : u'unknown',#评价总数
        u'bad_judge_times' : u'unknown',#差评比率
    }
    tb_consume_info = {
        u'total_amount' : u'unknown',
        u'total_consume_orders' : u'unknown',
        u'max_money' : u'unknown',
        u'min_money' : u'unknown',
        u'avg_money' : u'unknown',
        u'total_orders' : u'unknown',
        u'goods_nums' : u'unknown',
        u'back_goods_radio' : u'unknown',
        u'judge_times' : u'unknown',
        u'bad_judge_times' : u'unknown',
    }

    jd_addr_info = jd and jd.init_info_mp(basedata) or {}
    jd_addr_detail_list = []
    flag_list=[]
    for k,v in jd_addr_info.items():
        for it in v:
            if it['value'] not in flag_list:
                jd_addr_detail_list.append({
                    u'host_goods' : k,#收货人
                    u'addr_in' : u'---',#所在地区
                    u'addr' : it['value'],#地址
                    u'phone' : it['phone'],#手机
                    u'tel_phone' : it['tel_phone'] or '---',#固定手机
                    u'email' : it['email'] or '---',#电子邮箱
                    u'first_send_time' : u'---',#第一次送货时间
                    u'last_send_time' : u'---',#最后一个送货时间
                    u'order_nums' : u'---',#订单数
                    u'consume_amount' : u'---',#消费总额
                    u'source' : u'京东',#来源
                })
                flag_list.append(it['value'])
    tb_addr_detail_list = [{
        u'host_goods' : u'unknown',
        u'addr_in' : u'unknown',
        u'addr' : u'unknown',
        u'phone' : u'unknown',
        u'tel_phone' : u'unknown',
        u'email' : u'unknown',
        u'first_send_time' : u'unknown',
        u'last_send_time' : u'unknown',
        u'order_nums' : u'unknown',
        u'consume_amount' : u'unknown',
        u'source' : u'淘宝'
    }]

    jd_limit_amount_info = {
        u'limit_amount':bjd and bjd.baitiao[u'totalAmount'] or u'unknown',#白条额度
        u'limit_last_amount':bjd and bjd.baitiao[u'avaliableAmount'] or u'unknown',#白条剩余额度
        u'limit_consume_amount':bjd and bjd.baitiao[u'consumeAmount'] or u'unknown',#白条可用额度
        u'zm_credit_score':u'unknown',#芝麻信用分数
        u'hb_amount':u'unknown',#花呗额度
    }
    tb_limit_amount_info = {
        u'limit_amount':u'unknown',#白条额度
        u'limit_last_amount':u'unknown',#白条剩余额度
        u'limit_consume_amount':u'unknown',
        u'zm_credit_score':u'unknown',#芝麻信用分数
        u'hb_amount':u'unknown',#花呗额度
    }
    
    tb_valid_info = {
        u'same_with_lovelife' : u'unknown',#实名认证是否与美信生活实名认证一致
    }
    jd_valid_info = {
        u'same_with_lovelif' : u'unknown',
    }
    
    jd_addr_info = {
        u'userphone_in_addr' : jd and jd.min_rule_map[30007].feature_val or u'unknown',#收获人中是否有申请人
        u'addr_diff_nums' : jd and jd.min_rule_map[30008].feature_val or u'unknown',#不同的收货地址个数
        u'phone_in_contact' : jd and jd.min_rule_map[30009].feature_val or u'unknown',#收件人出现在通讯录中
        u'contact_sms' : jd and jd.min_rule_map[30010].feature_val or u'unknown',#与收件人有短信联系
        u'ul_in_addr': jd and jd.min_rule_map[30012].feature_val or u'unknown',#申请用户手机归属地出现在收货地址中
        u'contact_call' : jd and jd.min_rule_map[30011].feature_val or u'unknown' #与收件人有电话联系
    }
    tb_addr_info={
        u'userphone_in_addr' : u'unknown',
        u'addr_diff_nums' : u'unknown',
        u'phone_in_contact' : u'unknown',
        u'contact_sms' : u'unknown',
        u'ul_in_addr': u'unknown',
        u'contact_call' : u'unknown'
    }
    

    map_info={}
    month_map_info = {}
    stage_map_info = { u'af':0,u'bf':0,'cf':0,'df':0,'ef':0,'ff':0,'gf':0,'hf':0,'if':0,'lf':0,'mf':0,'nf':0 }
    jd_order_info=[]
    ll=[]
    for it in consume_list:
        key=it['time'].date()
        key_str=str(key).split('-')
        kk = key_str[0]+'-'+key_str[1]
        money=it['money']

        if money<=50:
            stage_map_info[u'af']+=1
        elif money>50 and money<=100:
            stage_map_info[u'bf']+=1
        elif money>100 and money<=200:
            stage_map_info[u'cf']+=1
        elif money>200 and money<=500:
            stage_map_info[u'df']+=1
        elif money>500 and money<=1000:
            stage_map_info[u'ef']+=1
        elif money>1000 and money<=3000:
            stage_map_info[u'ff']+=1
        elif money>3000 and money<=8000:
            stage_map_info[u'gf']+=1
        elif money>8000:
            stage_map_info[u'hf']+=1

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
                u'order_date':str(k),#订单日期
                u'goods_name':u'---',#商品名称
                u'goods_nums':str(map_info[k]['pac_num']),#商品件数
                u'amount':str(map_info[k]['amount']),#总额
                u'pay_ways': u'---',#支付方式
                u'addr': u'---',#收货地址
                u'host_goods':u'---'#收货人
            })
            ll.append(k)
    tb_order_info={
        u'order_date':u'unknown',
        u'goods_name':u'unknown',
        u'goods_nums':u'unknown',
        u'amount':u'unknown',
        u'pay_ways': u'unknown',
        u'addr': u'unknown',
        u'host_goods':u'unknown'
    }
    #汇集
    info = {
        u'base_info' : {    #基本信息
            u'jd':jd_basic_info,
            u'tb':tb_basic_info
        },
        u'amount' : {   #额度
            u'jd' : jd_limit_amount_info,
            u'tb' : {},
            #u'淘宝' : tb_limit_amount_info
        },
        u'lovelife' :{   #美信认证
            u'jd':jd_valid_info,
            u'tb':tb_valid_info
        },
        u'consume_record' :{    #消费金额
            u'jd':jd_consume_info,
            u'tb':tb_consume_info
        },
        u'host_goods': {    #收件人分析
            u'jd':jd_addr_detail_list,
            u'tb':tb_addr_detail_list
        },
        #u'addr':{   #
        #    u'jd':jd_addr_info,
        #    u'tb':tb_addr_info
        #},
        u'graph':{  #图表
            u'jd':{
                u'data1':stage_map_info,
                u'data2':month_map_info,
            },
            u'tb':{
                u'data1':{},
                u'data2':{}
            }
        },
        u'order_record':{   #订单记录
            u'jd': jd_order_info,
            u'tb': tb_order_info
        }
    }
    return info



'''通讯录'''
def init_contact_info(basedata,postloan):

    contact_list = basedata and basedata.contacts or []
    clen=len(contact_list) or 1
    upl=basedata and basedata.user_plocation or ''
    hl=basedata and basedata.home_location or ''
    lcmap={}
    for c in contact_list:
        city=c.phone_location.split('-')[0]
        if city not in lcmap:
            lcmap[city]=0
        lcmap[city]+=1
        lcmap[city]=lcmap[city]*100/clen
    #排序
    tup=sorted(lcmap.items(), key=lambda lcmap: lcmap[1],reverse=True)
    same_with_pl_info = {
        u'ul_radio' :{ it[0]:'%.2f'%(it[1]*1.0/clen)++str('%') for it in tup } 
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
            u'name':c.name,#称呼
            u'phone' : c.phone,#电话
            u'phone_location' : c.phone_location,#归属地
            u'remarks' : u'---'#备注
        }
        if c.phone in relatives_map: 
            relative_info.append(temp_c)
        else:
            contact_info.append(temp_c)
    clist=[]
    clist_none=[]

    #根据name排序
    for c in contact_info:
        if c.name != u'none':
            clist.append(c)
        else:
            clist_none.append(c)

    clist.extend( clist_none )
    info = {
        u'part_contatcs':same_with_pl_info,#通讯录
        u'relatives' : relative_info,#亲属
        u'view_contacts' : clist #通讯录总览
    }

    return info

'''通话记录'''
def init_sp_record_info(basedata,sp,p):
    
    bas_info=json.loads(basedata.sp and basedata.sp.base_info or '{}')
    data=bas_info and bas_info['data'] or {}
    basic_info={
        u'pass_sp' : u'unknown',#运营商实名认证
        u'name_in_sp':u'unknown',#运营商实名与自有实名是否一致
        u'startime' : u'unknown',#入网时间
        u'addr' : data and data['address'] or u'unknown',#地址
        u'netage' : data and data['netAge'] or u'unknown', #网龄
        u'left_amount': u'unknown',#账户余额
        u'first_call_time':u'unknown',#最早一次通话时间
        u'last_call_time' : u'unknown' #最后一次通话时间
    }


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
            u'phone_in_contact' : call.username !=u'none' and u'匹配' or u'未匹配',#通讯录匹配
            u'phone' : key,#号码
            u'call_duration' : str(call.call_duration),#通话时间
            u'call_times' : str(call_map[key][u'call_count']),#通话次数
            u'phone_location' : call.phone_location,#归属地
            u'call_in' : str(call_map[key][u'call_in']),#被叫次数
            u'call_out' : str(call_map[key][u'call_out']) #主叫次数
        })
    #自定义排序　通话时间，通话次数，主叫次数排序    
    def _key_of_sort(dic):
        return dic[u'call_duration'],dic[u'call_times'],dic[u'call_out']
    call_info.sort(key=_key_of_sort,reverse=True)

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
        u'shutdown_phone':u'unknown',#长时间关机（连续3天无数据、无通话、无短信记录
        u'call_law': u'unknown',#呼叫法院相关号码
        u'user_in_netloan':u'unknown',#申请人号码是否出现在网贷黑名单上
    }    


    contact_info ={
        u'call_len' : sp and sp.min_rule_map[20001].feature_val or u'unknown',#通话记录长度
        u'sms_len' : sp and sp.min_rule_map[20002].feature_val or u'unknown',#短信记录长度
        u'callout_times' : sp and sp.min_rule_map[20006].feature_val or u'unknown',#半年内主叫次数
        u'call_duration' : sp and sp.min_rule_map[20007].feature_val or u'unknown',#半年内主叫时长
        u'callin_times' : sp and sp.min_rule_map[20008].feature_val or u'unknown',#半年内被叫次数
        u'callin_duration' : sp and sp.min_rule_map[20009].feature_val or u'unknown',#半年内被叫时长
        u'rlen' : p and p.min_rule_map[50006].feature_val or u'unknown',#亲属长度
        u'relative_in_idl' : p and p.min_rule_map[50007].feature_val or u'unknown',#亲属在老家的个数
        u'rcall_len' : p and p.min_rule_map[50008].feature_val or u'unknown',#亲属通话时长
        u'rcall_times' : p and p.min_rule_map[50009].feature_val or u'unknown'#亲属通话次数
    }
        

    consume_level_info={
        u'incharge_amount':sp and sp.min_rule_map[20003].feature_val or u'unknown',#半年内充值金额
        u'incharge_times':sp and sp.min_rule_map[20004].feature_val or u'unknown',#半年内充值次数
        u'avg_incharge_inter' : sp and sp.min_rule_map[20005].feature_val or u'unknown',#半年内平均充值间隔
        u'avg_month_consume' : sp and float(sp.min_rule_map[20003].source)/6.0 or u'unknown'#月均消费
    }


    basic_info_month=[]    
    for k,v in month_info.items():
        basic_info_month.append({
            u'month' : key,#月份
            u'callout_duration':str(v[u'call_out']/60),#主叫时间
            u'callin_duration' :str(v[u'call_in']/60),#被叫时间
            u'sms_nums' : str(v[u'message']),#短信数量
            u'call_bill' : str(v[u'consume']),#话费消费
        })

    info = {
        u'basic_one' : basic_info,#基本信息
        u'basic_two' : no_arrearage_info,#基本信息
        u'call_record' : call_info,#通话记录
        u'person_closeness' : contact_info,#人际交往密切程度
        u'consume_month' : consume_level_info,#近期月均消费水平
        u'sp_consume_month' : basic_info_month,#运营商月消费
    }

    return info

