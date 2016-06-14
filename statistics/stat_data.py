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
        '1007' : { u'是否实名认证' : u'unknown'},#是否实名认证
        '1006' : { u'姓名' : u'unknown' },#姓名
        '1005' : { u'身份证号' : basedata.idcard_info['idcard'] },#idcardno
        '1004' : { u'性别' : basedata.idcard_info['sex'] },#性别
        '1003' : { u'年龄' : basedata.idcard_info['age'] },#年龄
        '1002' : { u'身份证所在地' : basedata.idcard_info['home_location'] },#身份证所在地
        '1001' : { u'申请人身份证号码是否出现在法院黑名单上' : u'unknown' } #申请人身份证号码是否出现在法院黑名单上
    }

'''电商分析'''
def init_online_shop_info(basedata,jd,tb):
    bjd = basedata and basedata.jd or None
    btb = basedata and basedata.tb or None
    login_his = jd and jd.login_his_map.keys() or []
    login_his.sort()

    #基本信息
    basic_info_list=[
        {
            '1008':u'电商名',
            '1007':u'会员名',
            '1006':u'等级',
            '1005':u'是否实名',
            '1004':u'绑定手机',
            '1003':u'登陆邮箱',
            '1002':u'最后一次登陆时间',
            '1001':u'使用时间'
        },
        {
            '1008':u'京东',
            '1007':bjd and bjd.jd_login_name or u'unknown',#会员名    
            '1006':bjd and bjd.user_level or u'unknown',#会员等级
            '1005':jd and jd.min_rule_map[30001].feature_val or u'unknown',#是否通过姓名验证
            '1004':bjd and bjd.phone_verifyied and bjd.phone_verifyied.values()[1] or u'unknown',#绑定手机号
            '1003':bjd and bjd.email_host.replace('\r\n','') or u'unknown',#登陆邮箱
            '1002':len(login_his)>0 and login_his[-1] or u'unknown',#最后一次登陆时间
            '1001':u'unknown' #使用时间
        },
        {
            '1008':u'淘宝',
            '1007':btb and btb.username or u'uknown',
            '1006':btb and btb.creditLevel or u'unknown',
            '1005':tb and tb.min_rule_map[40002].feature_val or u'unknown',
            '1004':btb and btb.bindMobile or u'unknown',
            '1003':btb and btb.loginEmail or u'unknown',
            '1002':u'---',
            '1001':u'---'
        },
    ]
    #白条
    baitiao_info_map = {
        '1007':{ u'京东白条额度':bjd and bjd.baitiao and bjd.baitiao[u'totalAmount'] or u'unknown' },#白条额度
        '1006':{ u'剩余额度':bjd and bjd.baitiao and bjd.baitiao[u'avaliableAmount'] or u'unknown' },#白条剩余额度
        '1005':{ u'累积消费':bjd and bjd.baitiao and bjd.baitiao[u'consumeAmount'] or u'unknown'},#白条可用额度
        '1004':{ u'芝麻信用分数':u'unknown' },#芝麻信用分数
        '1003':{ u'花呗额度':btb and btb.huabeiTotalAmount or u'unknown'},#花呗额度
        '1002':{ u'京东实名认证是否与美信生活实名认证一致' : u'---' },
        '1001':{ u'淘宝实名认证是否与美信生活实名认证一致' : u'---' },
    }

    #消费统计
    consume_list = jd and jd.consume_list or []
    tb_consume_list = tb and tb.harf_order_list or []
    jd_cm_list = [ it['money'] for it in consume_list ]
    tb_cm_list = [ float(it['orderTotalPrice']) for it in tb_consume_list ]
    tb_product_list = [ len(it['orderProducts']) for it in tb_consume_list]
    #排序
    jd_cm_list.sort()
    tb_cm_list.sort()
    consume_info_list = [
        {
            '10001' : u'电商名',
            '10002' : u'累计消费总额',
            '1009' : u'累计消费笔数',
            '1008' : u'单笔最高消费',
            '1007' : u'单笔最低消费',
            '1006' : u'平均每笔消费',
            '1005' : u'累计订单总数',
            '1004' : u'商品总件数',
            '1003' : u'返修退换货比率',
            '1002' : u'评价总数',
            '1001' : u'差评比率',
        },
        {
            '10001' : u'京东',
            '10002' : sum(jd_cm_list),#累计消费总额
            '1009' : len(jd_cm_list),#累计消费笔数
            '1008' : len(jd_cm_list) and jd_cm_list[-1] or u'---',#单笔最高消费
            '1007' : len(jd_cm_list) and jd_cm_list[0] or u'---',#单笔最低消费
            '1006' : sum(jd_cm_list)/(len(jd_cm_list) or 1),#平均每笔消费
            '1005' : len(jd_cm_list),#累计订单总数
            '1004' : u'unknown',#商品总件数
            '1003' : u'unknown',#返修退换货比率
            '1002' : u'unknown',#评价总数
            '1001' : u'unknown',#差评比率
        },
        {
            '10001' : u'淘宝',
            '10002' : sum(tb_cm_list),
            '1009' : len(tb_cm_list),
            '1008' : len(tb_cm_list) and tb_cm_list[-1] or u'---',
            '1007' : len(tb_cm_list) and tb_cm_list[0] or u'---',
            '1006' : sum(tb_cm_list)/(len(tb_cm_list) or 1),
            '1005' : len(tb_cm_list),
            '1004' : sum(tb_product_list),
            '1003' : u'---',
            '1002' : u'---',
            '1001' : u'---',
        }
    ]
    
    #京东收货人分析
    jd_addr_info = jd and jd.init_info_mp(basedata) or {}
    flag_list=[]
    
    jd_addr_detail_list=[{
        '10001' : u'收货人',
        '10002' : u'所在地区',
        '1009' : u'地址',
        '1008' : u'手机',
        '1007' : u'固定手机',
        '1006' : u'邮箱',
        '1005' : u'第一次送货时间',
        '1004' : u'最后一次送货时间',
        '1003' : u'订单数',
        '1002' : u'消费总额',
        '1001' : u'来源'
    }]

    for k,v in jd_addr_info.items():
        for it in v:
            if it['dictr'] not in flag_list:
                jd_addr_detail_list.append({
                    '10001' : k,#收货人
                    '10002' : it['dictr'],#所在地区
                    '1009' :  it['address'],#地址
                    '1008' : it['phone'],#手机
                    '1007' : it['tel_phone'] or '---',#固定手机
                    '1006' : it['email'] or '---',#电子邮箱
                    '1005' : u'---',#第一次送货时间
                    '1004' : u'---',#最后一个送货时间
                    '1003' : u'---',#订单数
                    '1002' : u'---',#消费总额
                    '1001' : u'京东',#来源
                })
                flag_list.append(it['dictr'])
    if len(jd_addr_detail_list)<=1:
        jd_addr_detail_list.append({
            '10001' : u'---',
            '10002' : u'---',
            '1009' : u'---',
            '1008' : u'---',
            '1007' : u'---',
            '1006' : u'---',
            '1005' : u'---',
            '1004' : u'---',
            '1003' : u'---',
            '1002' : u'---',
            '1001' : u'京东'
        })

    #淘宝收货人分析
    tb_addr_info = tb and tb.address_map or {}
    flag_list = []
    tb_addr_detail_list = [
        {
            '10001' : u'收货人',
            '10002' : u'所在地区',
            '1009' : u'地址',
            '1008' : u'手机',
            '1007' : u'固定手机',
            '1006' : u'邮箱',
            '1005': u'第一次送货时间',
            '1004' : u'最后一次送货时间',
            '1003' : u'订单数',
            '1002' : u'消费总额',
            '1001' : u'来源'
        }
    ]
    for k,v in tb_addr_info.items():
        for it in v:
            if it['dictr'] not in flag_list:
                tb_addr_detail_list.append({
                    '10001' : k,#收货人
                    '10002' : it['dictr'],#所在地区
                    '1009' :  it['address'],#地址
                    '1008' : it['phone'],#手机
                    '1007' : it['tel_phone'] or '---',#固定手机
                    '1006' : it['email'] or '---',#电子邮箱
                    '1005' : u'---',#第一次送货时间
                    '1004' : u'---',#最后一个送货时间
                    '1003' : u'---',#订单数
                    '1002' : u'---',#消费总额
                    '1001' : u'淘宝',#来源
                })
                flag_list.append(it['dictr'])
    if len(tb_addr_detail_list)<=1:
        tb_addr_detail_list.append({
            '10001' : u'---',
            '10002' : u'---',
            '1009' : u'---',
            '1008' : u'---',
            '1007' : u'---',
            '1006' : u'---',
            '1005' : u'---',
            '1004' : u'---',
            '1003' : u'---',
            '1002' : u'---',
            '1001' : u'淘宝'
        })

    #图标数据    
    map_info={}
    #jd_month_map_info = {'Jan':0,'Feb':0,'Mar':0,'Apr':0,'May':0,'Jun':0,'Jul':0,'Aug':0,'Sep':0,'Oct':0,'Nov':0,'Dec':0}
    jd_month_map_info = {}
    jd_goods_cate_info = {}
    jd_stage_map_info = { u'Jan':0,u'Feb':0,'Mar':0,'Apr':0,'May':0,'Jun':0,'Jul':0,'Aug':0,'Sep':0,'Oct':0,'Nov':0,'Dec':0 }
    for it in consume_list:
        key=it['time'].date()
        key_str=str(key).split('-')
        kk = key_str[0]+'-'+key_str[1]
        money=it['money']

        if money<=50:
            jd_stage_map_info[u'Jan']+=1
        elif money>50 and money<=100:
            jd_stage_map_info[u'Feb']+=1
        elif money>100 and money<=200:
            jd_stage_map_info[u'Mar']+=1
        elif money>200 and money<=500:
            jd_stage_map_info[u'Apr']+=1
        elif money>500 and money<=1000:
            jd_stage_map_info[u'May']+=1
        elif money>1000 and money<=3000:
            jd_stage_map_info[u'Jun']+=1
        elif money>3000 and money<=8000:
            jd_stage_map_info[u'Jul']+=1
        elif money>8000:
            jd_stage_map_info[u'Aug']+=1

        if kk not in jd_month_map_info:
            jd_month_map_info[kk]=0
        if kk in str(key):
            jd_month_map_info[kk]+=it['money']

        if key not in map_info:
            map_info[key]={'amount':0,'pac_num':0}
        map_info[key]['amount']+=it['money']
        map_info[key]['pac_num']+=1
    #淘宝图标数据
    tb_month_map_info = {}
    tb_goods_cate_info = {}
    tb_stage_map_info = { u'Jan':0,u'Feb':0,'Mar':0,'Apr':0,'May':0,'Jun':0,'Jul':0,'Aug':0,'Sep':0,'Oct':0,'Nov':0,'Dec':0 } 
    for it in tb_consume_list:

        key=it['businessDate']
        key_str=key.split('-')
        kk = key_str[0]+'-'+key_str[1]
        money=float(it['orderTotalPrice'])

        if money<=50:
            tb_stage_map_info[u'Jan']+=1
        elif money>50 and money<=100:
            tb_stage_map_info[u'Feb']+=1
        elif money>100 and money<=200:
            tb_stage_map_info[u'Mar']+=1
        elif money>200 and money<=500:
            tb_stage_map_info[u'Apr']+=1
        elif money>500 and money<=1000:
            tb_stage_map_info[u'May']+=1
        elif money>1000 and money<=3000:
            tb_stage_map_info[u'Jun']+=1
        elif money>3000 and money<=8000:
            tb_stage_map_info[u'Jul']+=1
        elif money>8000:
            tb_stage_map_info[u'Aug']+=1

        if kk not in tb_month_map_info:
            tb_month_map_info[kk]=0
        if kk in str(key):
            tb_month_map_info[kk] += money

    #京东订单记录
    ll = []
    jd_order_info=[
        {
            '1007' : u'订单日期',
            '1006' : u'商品名称',
            '1005' : u'商品件数',
            '1004' : u'总额',
            '1003' : u'支付方式',
            '1002' : u'收货人地址',
            '1001' : u'收货人',
        }
    ]
    for it in consume_list:
        k=it['time'].date()
        if k not in ll:
            jd_order_info.append({
                '1007':str(k),#订单日期
                '1006':u'---',#商品名称
                '1005':str(map_info[k]['pac_num']),#商品件数
                '1004':str(map_info[k]['amount']),#总额
                '1003': u'---',#支付方式
                '1002': u'---',#收货地址
                '1001':u'---'#收货人
            })
            ll.append(k)

    if len(jd_order_info)<=1:
        jd_order_info.append({
                '1007' : u'---',
                '1006' : u'---',
                '1005' : u'---',
                '1004' : u'---',
                '1003' : u'---',
                '1002' : u'---',
                '1001' : u'---'
            }
        )
    #淘宝订单记录
    hl = tb and tb.harf_order_list or []
    hl_map = {}
    for it in hl:
        key=it['businessDate']
        if key not in hl_map:
            hl_map[key]=it
        else:
            hl_map[key]['orderProducts'].extend(it['orderProducts'])
            price=float(hl_map[key]['orderTotalPrice']) + float(it['orderTotalPrice'])
            hl_map[key]['orderTotalPrice'] = str(price)

    tb_order_info = [
        {
            '1007' : u'订单日期',
            '1006' : u'商品名称',
            '1005' : u'商品件数',
            '1004' : u'总额',
            '1003' : u'支付方式',
            '1002' : u'收货人地址',
            '1001' : u'收货人',
        }
    ]
    for k,v in hl_map.items():
        tb_order_info.append({
                '1007': k,
                '1006' : '<br/>'.join([ p['productName'] for p in v['orderProducts']]),
                '1005' : len(v['orderProducts']),
                '1004' : v['orderTotalPrice'],
                '1003' : u'---',
                '1002' : u'---',
                '1001' : u'---'
        })
    if len(tb_order_info)<=1:
        tb_order_info.append({
                '1007' : u'---',
                '1006' : u'---',
                '1005' : u'---',
                '1004' : u'---',
                '1003' : u'---',
                '1002' : u'---',
                '1001' : u'---'
            }
        )

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
                u'order_amount':jd_stage_map_info,
                u'goods_cate' : jd_goods_cate_info,
                u'month_consume':jd_month_map_info,
            },
            u'tb':{
                u'order_amount':tb_stage_map_info,
                u'goods_cate':tb_goods_cate_info,
                u'month_consume':tb_month_map_info,
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
    lc={ k:v*100.0/clen for k,v in lcmap.items()}
    #排序
    tup=sorted(lc.items(), key=lambda lc:lc[1],reverse=True)
    same_with_pl_info = [
        {
            '1002':u'归属地',
            '1001':u'联系人归属地占比'
        },
    ]
    for it in tup:
        same_with_pl_info.append({
            '1002':it[0],
            '1001':'%.2f'%(it[1])+str('%')
        })
    if len(same_with_pl_info)<=1:
        same_with_pl_info.append({
            '1002':'---',
            '1001':'---'
        })
    #亲属
    relative_info = [
        {
            '1004':u'称呼',
            '1003':u'电话',
            '1002':u'归属地',
            '1001':u'备注'
        },
    ]
    contact_info = []
    relatives_map={}
    relatives_map.update(postloan and postloan.father_mp or {})
    relatives_map.update(postloan and postloan.mather_mp or {})
    relatives_map.update(postloan and postloan.home_mp or {})
    relatives_map.update(postloan and postloan.r_relative_map or {})
    
    contact_info=[
        {
            '1004':u'称呼',
            '1003':u'电话',
            '1002':u'归属地',
            '1001':u'备注'
        }
    ]
    for c in contact_list:
        temp_c={
            '1004' : c.name,#称呼
            '1003' : c.phone,#电话
            '1002' : c.phone_location,#归属地
            '1001': u'---'#备注
        }
        if c.phone in relatives_map: 
            relative_info.append(temp_c)
        else:
            contact_info.append(temp_c)
    #default
    if len(contact_info)<=1:
        contact_info.append({
                '1004' : u'---',
                '1003' : u'---',
                '1002' : u'---',
                '1001' : u'---'
            }
        )
    #relative default
    if len(relative_info)<=1:
        relative_info.append({
                '1004' : u'---',
                '1003' : u'---',
                '1002' : u'---',
                '1001' : u'---'
            }
        )

    clist=[]
    clist_none=[]
    
    #根据name排序
    if len(contact_info)>=2:
        for c in contact_info:
            if c['1004'] != u'none':
                clist.append(c)
            else:
                clist_none.append(c)
        clist.extend( clist_none )
    info = {
        u'part_contatcs':same_with_pl_info,#通讯录
        u'relatives' : relative_info,#亲属
        u'view_contacts' : clist or contact_info #通讯录总览
    }
    return info

'''通话记录'''
def init_sp_record_info(basedata,sp,p):

    #基本信息
    bas_info=basedata.sp and basedata.sp.personalInfo or {}
    data = bas_info and bas_info['data'] or {}
    basic_info={
        '1007':{ u'运营商实名认证' : u'---' },#运营商实名认证
        '1006':{ u'运营商实名与美信生活实名是否一致':u'---' },#运营商实名与自有实名是否一致
        '1005':{ u'入网时间' : u'---' },#入网时间
        '1004':{ u'地址' : data and data['address'] or u'---' },#地址
        '1003':{ u'网龄' : data and data['netAge'] or u'---' }, #网龄
        '1002':{ u'最早一次通话时间':u'---' },#最早一次通话时间
        '1001':{ u'最后一次通话时间' : u'---' } #最后一次通话时间
    }
    #关键指标
    no_arrearage_info = {
        '1003':{ u'长时间关机（连续3天无数据、无通话、无短信记录)':u'---' },
        '1002':{ u'呼叫法院相关号码': u'---' },
        '1001':{ u'申请人号码是否出现在网贷黑名单上':u'---' },
    }

    #人际交往密切程度

    contact_info ={
        '10001':{ u'半年通话记录长度' : sp and sp.min_rule_map[20001].feature_val or u'unknown' },#通话记录长度
        '1009':{ u'半年短信记录长度' : sp and sp.min_rule_map[20002].feature_val or u'unknown'},#短信记录长度
        '1008':{ u'半年内主叫次数' : sp and sp.min_rule_map[20006].feature_val or u'unknown' },#半年内主叫次数
        '1007':{ u'半年内主叫时长' : sp and sp.min_rule_map[20007].feature_val or u'unknown' },#半年内主叫时长
        '1006':{ u'半年内被叫次数' : sp and sp.min_rule_map[20008].feature_val or u'unknown' },#半年内被叫次数
        '1005':{ u'半年内被叫时长' : sp and sp.min_rule_map[20009].feature_val or u'unknown' },#半年内被叫时长
        '1004':{ u'亲属长度' : p and p.min_rule_map[50006].feature_val or u'unknown' },#亲属长度
        '1003':{ u'亲属在老家个数' : p and p.min_rule_map[50007].feature_val or u'unknown' },#亲属在老家的个数
        '1002':{ u'半年亲属通话时长' : p and p.min_rule_map[50008].feature_val or u'unknown' },#亲属通话时长
        '1001':{ u'半年亲属通话次数' : p and p.min_rule_map[50009].feature_val or u'unknown' }#亲属通话次数
    }

    #近期消费水平
    consume_level_info={
        '1004':{ u'半年内充实金额':sp and sp.min_rule_map[20003].feature_val or u'unknown'},#半年内充值金额
        '1003':{ u'半年内充实次数':sp and sp.min_rule_map[20004].feature_val or u'unknown'},#半年内充值次数
        '1002':{ u'半年内平均充值间隔':sp and sp.min_rule_map[20005].feature_val or u'unknown'},#半年内平均充值间隔
        '1001':{ u'月均消费' : sp and float(sp.min_rule_map[20003].source)/6.0 or u'unknown' }#月均消费
    }


    #通话记录
    sp_calls = basedata and basedata.sp_calls or []
    call_map={}
    month_info={}

    for call in sp_calls:
        if call.phone not in call_map:
            call_map[call.phone]={u'call_in':0,u'call_out':0,u'call_count':0,u'call_duration':0}
        if u'主叫' in call.call_type:
            call_map[call.phone][u'call_out'] +=1
        elif u'被叫' in call.call_type:
            call_map[call.phone][u'call_in'] +=1
        call_map[call.phone][u'call_count'] += 1
        call_map[call.phone][u'call_duration'] += call.call_duration
        #按月统计
        key=str(call.call_time.year)+'-'+str(call.call_time.month<10 and '0'+str(call.call_time.month) or call.call_time.month)
        if key not in month_info:
            month_info[key]={
                u'call_out':0,
                u'call_in':0,
                u'message':0,
                u'consume':0,
            }    
        if key in str(call.call_time):
            if u'主叫' in call.call_type:
                month_info[key][u'call_out']+=call.call_duration
            elif u'被叫' in call.call_type:
                month_info[key][u'call_in']+=call.call_duration

    sms_list =  basedata and basedata.sp_sms or []            
    for msg in sms_list:
        key=str(msg.send_time.year)+'-'+str(msg.send_time.month<10 and '0'+str(msg.send_time.month) or msg.send_time.month)
        if key in month_info:
            month_info[key][u'message']+=1

    call_info=[
        {
            '1007':u'通讯录匹配',
            '1006':u'号码',
            '1005':u'通话时间',
            '1004':u'通话次数',
            '1003':u'归属地',
            '1002':u'被叫次数',
            '1001':u'主叫次数'
        }
    ]
    call_info_content =[]
    flag_list = []
    for call in sp_calls:
        key=call.phone
        if key not in flag_list:
            call_info_content.append({
                '1007' : call.username,#通讯录匹配
                '1006' : key,#号码
                '1005' : str(call_map[key][u'call_duration']),#通话时间
                '1004' : str(call_map[key][u'call_count']),#通话次数
                '1003' : str(call.phone_location),#归属地
                '1002' : str(call_map[key][u'call_in']),#被叫次数
                '1001' : str(call_map[key][u'call_out']) #主叫次数
            })
            flag_list.append(key)
    #自定义排序　通话时间，通话次数，主叫次数排序    
    def _key_of_sort(dic):
        return int(dic['1005']),int(dic['1004']),int(dic['1001'])
    call_info_content.sort(key=_key_of_sort,reverse=True)
    call_info.extend( call_info_content )
    if len(call_info)<=1:
        call_info.append({
            '1007':u'---',
            '1006':u'---',
            '1005':u'---',
            '1004':u'---',
            '1003':u'---',
            '1002':u'---',
            '1001':u'---'
        })

    #月消费汇总
    basic_info_month=[
        {
            '1005':u'月份',
            '1004':u'主叫时间',
            '1003':u'被叫时长',
            '1002':u'短息数量',
            '1001':u'话费消费',
        }
    ]
    for k,v in month_info.items():
        basic_info_month.append({
            '1005' : k,#月份
            '1004' : str(v[u'call_out']/60),#主叫时间
            '1003' : str(v[u'call_in']/60),#被叫时间
            '1002' : str(v[u'message']),#短信数量
            '1001' : str(v[u'consume']),#话费消费
        })
    if len(basic_info_month)<=1:
        basic_info_month.append({
                '1005':u'---',
                '1004':u'---',
                '1003':u'---',
                '1002':u'---',
                '1001':u'---',
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

