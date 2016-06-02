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
        '1':{ u'是否实名认证' : u'unknown'},#是否实名认证
        '2':{ u'姓名' : u'unknown' },#姓名
        '3':{ u'身份证号' : basedata.idcard_info['idcard'] },#idcardno
        '4':{ u'性别' : basedata.idcard_info['sex'] },#性别
        '5':{ u'年龄' : basedata.idcard_info['age'] },#年龄
        '6':{ u'身份证所在地' : basedata.idcard_info['home_location'] },#身份证所在地
        '9':{ u'申请人身份证号码是否出现在法院黑名单上' : u'unknown' } #申请人身份证号码是否出现在法院黑名单上
    }

'''电商分析'''
def init_online_shop_info(basedata,jd):
    bjd = basedata and basedata.jd or None
    login_his = jd and jd.login_his_map.keys() or []
    login_his.sort()

    #基本信息
    basic_info_list=[
        {
            '1':u'电商名',
            '2':u'会员名',
            '3':u'等级',
            '4':u'是否实名',
            '5':u'绑定手机',
            '6':u'登陆邮箱',
            '7':u'最后一次登陆时间',
            '8':u'使用时间'
        },
        {
            '1':u'京东',
            '2':bjd and bjd.jd_login_name or u'unknown',#会员名    
            '3':bjd and bjd.user_level or u'unknown',#会员等级
            '4':jd and jd.min_rule_map[30001].feature_val or u'unknown',#是否通过姓名验证
            '5':u'unknown',#绑定手机号
            '6':bjd and bjd.email_host.replace('\r\n','') or u'unknown',#登陆邮箱
            '7':len(login_his)>0 and login_his[-1] or u'unknown',#最后一次登陆时间
            '8':u'unknown' #使用时间
        },
        {
            '1':u'淘宝',
            '2':u'---',
            '3':u'---',
            '4':u'---',
            '5':u'---',
            '6':u'---',
            '7':u'---',
            '8':u'---'
        },
    ]
    #白条
    baitiao_info_map = {
        '1':{ u'京东白条额度':bjd and bjd.baitiao[u'totalAmount'] or u'unknown' },#白条额度
        '2':{ u'剩余额度':bjd and bjd.baitiao[u'avaliableAmount'] or u'unknown' },#白条剩余额度
        '3':{ u'累积消费':bjd and bjd.baitiao[u'consumeAmount'] or u'unknown'},#白条可用额度
        '4':{ u'芝麻信用分数':u'unknown' },#芝麻信用分数
        '5':{ u'花呗额度':u'unknown' },#花呗额度
        '6':{ u'京东实名认证是否与美信生活实名认证一致' : u'---' },
        '7':{ u'淘宝实名认证是否与美信生活实名认证一致' : u'---' },
    }

    #消费统计
    consume_list = jd and jd.consume_list or []
    cm_list = [ it['money'] for it in consume_list ]
    cm_list.sort()
    consume_info_list = [
        {
            '1' : u'电商名',
            '2' : u'累计消费总额',
            '3' : u'累计消费笔数',
            '4' : u'单笔最高消费',
            '5' : u'单笔最低消费',
            '6' : u'平均每笔消费',
            '7' : u'累计订单总数',
            '8' : u'商品总件数',
            '9' : u'返修退换货比率',
            '10' : u'评价总数',
            '11' : u'差评比率',
        },
        {
            '1' : u'京东',
            '2' : jd and jd.min_rule_map[30005].feature_val or u'unknown',#累计消费总额
            '3' : jd and jd.min_rule_map[30006].feature_val or u'unknown',#累计消费笔数
            '4' : len(cm_list) and cm_list[-1] or u'unknown',#单笔最高消费
            '5' : len(cm_list) and cm_list[0] or u'unknown',#单笔最低消费
            '6' : (jd and float(jd.min_rule_map[30005].source) or 0)*1.0/(jd and float(jd.min_rule_map[30006].source) or 1),#平均每笔消费
            '7' : len(consume_list),#累计订单总数
            '8' : u'unknown',#商品总件数
            '9' : u'unknown',#返修退换货比率
            '10' : u'unknown',#评价总数
            '11' : u'unknown',#差评比率
        },
        {
            '1' : u'淘宝',
            '2' : u'---',
            '3' : u'---',
            '4' : u'---',
            '5' : u'---',
            '6' : u'unknown',
            '7' : u'unknown',
            '8' : u'unknown',
            '9' : u'unknown',
            '10' : u'unknown',
            '11' : u'unknown',
        }
    ]
    
    #京东收货人分析
    jd_addr_info = jd and jd.init_info_mp(basedata) or {}
    jd_addr_detail_list = []
    flag_list=[]
    
    jd_addr_detail_list=[{
        '1' : u'收货人',
        '2' : u'所在地区',
        '3' : u'地址',
        '4' : u'手机',
        '5' : u'固定手机',
        '6' : u'邮箱',
        '7' : u'第一次送货时间',
        '8' : u'最后一次送货时间',
        '9' : u'订单数',
        '10' : u'消费总额',
        '11' : u'来源'
    }]

    for k,v in jd_addr_info.items():
        for it in v:
            if it['value'] not in flag_list:
                jd_addr_detail_list.append({
                    '1' : k,#收货人
                    '2' : u'---',#所在地区
                    '3' : it['value'],#地址
                    '4' : it['phone'],#手机
                    '5' : it['tel_phone'] or '---',#固定手机
                    '6' : it['email'] or '---',#电子邮箱
                    '7' : u'---',#第一次送货时间
                    '8' : u'---',#最后一个送货时间
                    '9' : u'---',#订单数
                    '10' : u'---',#消费总额
                    '11' : u'京东',#来源
                })
                flag_list.append(it['value'])
    if len(jd_addr_detail_list)<=1:
        jd_addr_detail_list.append({
            '1' : u'---',
            '2' : u'---',
            '3' : u'---',
            '4' : u'---',
            '5' : u'---',
            '6' : u'---',
            '7' : u'---',
            '8' : u'---',
            '9' : u'---',
            '10' : u'---',
            '11' : u'京东'
        })

    #淘宝收货人分析
    tb_addr_detail_list = [
        {
            '1' : u'收货人',
            '2' : u'所在地区',
            '3' : u'地址',
            '4' : u'手机',
            '5' : u'固定手机',
            '6' : u'邮箱',
            '7': u'第一次送货时间',
            '8' : u'最后一次送货时间',
            '9' : u'订单数',
            '10' : u'消费总额',
            '11' : u'来源'
        },
        {
            '1' : u'---',
            '2' : u'---',
            '3' : u'---',
            '4' : u'---',
            '5' : u'---',
            '6' : u'---',
            '7' : u'---',
            '8' : u'---',
            '9' : u'---',
            '10' : u'---',
            '11' : u'淘宝'
        }
    ]

    #图标数据    
    map_info={}
    month_map_info = {}
    stage_map_info = { u'af':0,u'bf':0,'cf':0,'df':0,'ef':0,'ff':0,'gf':0,'hf':0,'if':0,'lf':0,'mf':0,'nf':0 }
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

    #京东订单记录
    jd_order_info=[
        {
            '1' : u'订单日期',
            '2' : u'商品名称',
            '3' : u'商品件数',
            '4' : u'总额',
            '5' : u'支付方式',
            '6' : u'收货人地址',
            '7' : u'收货人',
        }
    ]
    for it in consume_list:
        k=it['time'].date()
        if k not in ll:
            jd_order_info.append({
                '1':str(k),#订单日期
                '2':u'---',#商品名称
                '3':str(map_info[k]['pac_num']),#商品件数
                '4':str(map_info[k]['amount']),#总额
                '5': u'---',#支付方式
                '6': u'---',#收货地址
                '7':u'---'#收货人
            })
            ll.append(k)

    if len(jd_order_info)<=1:
        jd_order_info.append({
                '1' : u'---',
                '2' : u'---',
                '3' : u'---',
                '4' : u'---',
                '5' : u'---',
                '6' : u'---',
                '7' : u'---'
            }
        )

    tb_order_info = [
        {
            '1' : u'订单日期',
            '2' : u'商品名称',
            '3' : u'商品件数',
            '4' : u'总额',
            '5' : u'支付方式',
            '6' : u'收货人地址',
            '7' : u'收货人',
        }, 
        {
            '1': u'---',
            '2' : u'---',
            '3' : u'---',
            '4' : u'---',
            '5' : u'---',
            '6' : u'---',
            '7' : u'---'
        }
    ]
    #汇集
    info = {
        u'base_info' : basic_info_list,#基本信息
        u'baitiao_info' : baitiao_info_map,
        u'consume_record' : consume_info_list, #消费金额
        u'host_goods': {    #收件人分析
            u'jd':jd_addr_detail_list,
            u'tb':tb_addr_detail_list
        },
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
            u'tb': tb_order_info,
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
    same_with_pl_info = [
        {
            '1':u'归属地',
            '2':u'联系人归属地占比'
        }
    ]
    for it in tup:
        same_with_pl_info.append({
            it[0]:'%.2f'%(it[1]*1.0/clen)+str('%')
        })
    if len(same_with_pl_info)<=1:
        same_with_pl_info.append({
            '1':'---',
            '2':'---'
        })
    #亲属
    relative_info = [
        {
            '1':u'称呼',
            '2':u'电话',
            '3':u'归属地',
            '4':u'备注'
        }
    ]
    contact_info = []
    relatives_map={}
    relatives_map.update(postloan and postloan.father_mp or {})
    relatives_map.update(postloan and postloan.mather_mp or {})
    relatives_map.update(postloan and postloan.home_mp or {})
    relatives_map.update(postloan and postloan.r_relative_map or {})
    
    contact_info=[
        {
            '1':u'称呼',
            '2':u'电话',
            '3':u'归属地',
            '4':u'备注'
        }
    ]

    for c in contact_list:
        temp_c={
            '1' : c.name,#称呼
            '2' : c.phone,#电话
            '3' : c.phone_location,#归属地
            '4': u'---'#备注
        }
        if c.phone in relatives_map: 
            relative_info.append(temp_c)
        else:
            contact_info.append(temp_c)
    #default
    if len(contact_info)<=1:
        contact_info.append({
                '1' : u'---',
                '2' : u'---',
                '3' : u'---',
                '4' : u'---'
            }
        )
    #relative default
    if len(relative_info)<=1:
        relative_info.append({
                '1' : u'---',
                '2' : u'---',
                '3' : u'---',
                '4' : u'---'
            }
        )

    clist=contact_info
    clist_none=[]

    #根据name排序
    if len(contact_info)>2:
        for c in contact_info:
            if c[1] != u'none':
                clist.append(c)
            else:
                clist_none.append(c)
        clist.extend( clist_none )
    info = {
        u'part_contatcs':same_with_pl_info,#通讯录
        u'relatives' : relative_info,#亲属
        u'view_contacts' : clist  #通讯录总览
    }
    return info

'''通话记录'''
def init_sp_record_info(basedata,sp,p):

    #基本信息
    bas_info=json.loads(basedata.sp and basedata.sp.base_info or '{}')
    data=bas_info and bas_info['data'] or {}
    basic_info={
        '1':{ u'运营商实名认证' : u'unknown' },#运营商实名认证
        '2':{ u'运营商实名与美信生活实名是否一致':u'unknown' },#运营商实名与自有实名是否一致
        '3':{ u'入网时间' : u'unknown' },#入网时间
        '4':{ u'地址' : data and data['address'] or u'unknown' },#地址
        '5':{ u'网龄' : data and data['netAge'] or u'unknown' }, #网龄
        '6':{ u'最早一次通话时间':u'unknown' },#最早一次通话时间
        '7':{ u'最后一次通话时间' : u'unknown' } #最后一次通话时间
    }
    #关键指标
    no_arrearage_info = {
        '1':{ u'长时间关机（连续3天无数据、无通话、无短信记录)':u'unknown' },
        '2':{ u'呼叫法院相关号码': u'unknown' },
        '3':{ u'申请人号码是否出现在网贷黑名单上':u'unknown' },
    }

    #人际交往密切程度

    contact_info ={
        '1':{ u'半年通话记录长度' : sp and sp.min_rule_map[20001].feature_val or u'unknown' },#通话记录长度
        '2':{ u'半年短信记录长度' : sp and sp.min_rule_map[20002].feature_val or u'unknown'},#短信记录长度
        '3':{ u'半年内主叫次数' : sp and sp.min_rule_map[20006].feature_val or u'unknown' },#半年内主叫次数
        '4':{ u'半年内主叫时长' : sp and sp.min_rule_map[20007].feature_val or u'unknown' },#半年内主叫时长
        '5':{ u'半年内被叫次数' : sp and sp.min_rule_map[20008].feature_val or u'unknown' },#半年内被叫次数
        '6':{ u'半年内被叫时长' : sp and sp.min_rule_map[20009].feature_val or u'unknown' },#半年内被叫时长
        '7':{ u'亲属长度' : p and p.min_rule_map[50006].feature_val or u'unknown' },#亲属长度
        '8':{ u'亲属在老家个数' : p and p.min_rule_map[50007].feature_val or u'unknown' },#亲属在老家的个数
        '9':{ u'半年亲属通话时长' : p and p.min_rule_map[50008].feature_val or u'unknown' },#亲属通话时长
        '10':{ u'半年亲属通话次数' : p and p.min_rule_map[50009].feature_val or u'unknown' }#亲属通话次数
    }

    #近期消费水平
    consume_level_info={
        '1':{ u'半年内充实金额':sp and sp.min_rule_map[20003].feature_val or u'unknown'},#半年内充值金额
        '2':{ u'半年内充实次数':sp and sp.min_rule_map[20004].feature_val or u'unknown'},#半年内充值次数
        '3':{ u'半年内平均充值间隔':sp and sp.min_rule_map[20005].feature_val or u'unknown'},#半年内平均充值间隔
        '4':{ u'月均消费' : sp and float(sp.min_rule_map[20003].source)/6.0 or u'unknown' }#月均消费
    }


    #通话记录
    sp_calls = basedata and basedata.sp_calls or []
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


    call_info=[
        {
            '1':u'通讯录匹配',
            '2':u'号码',
            '3':u'通话时间',
            '4':u'通话次数',
            '5':u'归属地',
            '6':u'被叫次数',
            '7':u'主叫次数'
        }
    ]

    for call in sp_calls:
        key=call.phone
        call_info.append({
            '1' : call.username !=u'none' and u'匹配' or u'未匹配',#通讯录匹配
            '2' : key,#号码
            '3' : str(call.call_duration),#通话时间
            '4' : str(call_map[key][u'call_count']),#通话次数
            '5' : call.phone_location,#归属地
            '6' : str(call_map[key][u'call_in']),#被叫次数
            '7' : str(call_map[key][u'call_out']) #主叫次数
        })
    #自定义排序　通话时间，通话次数，主叫次数排序    
    def _key_of_sort(dic):
        return dic['3'],dic['4'],dic['7']
    call_info.sort(key=_key_of_sort,reverse=True)
    if len(call_info)<=1:
        call_info.append({
            '1':u'---',
            '2':u'---',
            '3':u'---',
            '4':u'---',
            '5':u'---',
            '6':u'---',
            '7':u'---'
        })

    
    #月消费汇总
    basic_info_month=[
        {
            '1':u'月份',
            '2':u'主叫时间',
            '3':u'被叫时长',
            '4':u'短息数量',
            '5':u'话费消费',
        }
    ]
    for k,v in month_info.items():
        basic_info_month.append({
            '1' : key,#月份
            '2' : str(v[u'call_out']/60),#主叫时间
            '3' : str(v[u'call_in']/60),#被叫时间
            '4' : str(v[u'message']),#短信数量
            '5' : str(v[u'consume']),#话费消费
        })
    if len(basic_info_month)<=1:
        basic_info_month.append({
                '1':u'---',
                '2':u'---',
                '3':u'---',
                '4':u'---',
                '5':u'---',
            }
        )

    info = {
        u'basic_info' : basic_info,#基本信息
        u'key_level' : no_arrearage_info,#关键指标
        u'person_closeness' : contact_info,#人际交往密切程度
        u'consume_month' : consume_level_info,#近期月均消费水平
        u'sp_consume_month' : basic_info_month ,#月消费汇总,
        u'call_info' : call_info,#通话记录
    }

    return info

