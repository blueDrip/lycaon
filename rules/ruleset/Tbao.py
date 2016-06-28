#!/usr/bin/env python
# encoding: utf-8
import sys
import os
from datetime import datetime,timedelta
from rules.models import BaseRule
from rules.raw_data import minRule
class Tbao(BaseRule):

    def __init__(self,basedata):
        self.harf_order_list = self.init_orderList(basedata)
        self.address_map = self.init_info_mp(basedata)

    def init_orderList(self,basedata):
        order_list = basedata.tb and basedata.tb.orderList or []
        now = basedata.create_time
        orderlist=[]
        for it in order_list:
            dt=it['businessDate'].split('-')
            dd= datetime(int(dt[0]),int(dt[1]),int(dt[2]))
            if dd>now-timedelta(180) and dd<now:
                orderlist.append(it)
        return orderlist

    #地址
    def init_info_mp(self,basedata):
        address_list = basedata.tb and basedata.tb.addrs or []
        infomp={}
        for adr in address_list:
            info = adr.replace('\t','').replace('\n','').split('|')
            key = len(info)>=1 and info[0] or None
            dictr = len(info)>=2 and info[1]or None
            address = len(info)>=3 and info[2] or None
            phone=len(info)>=4 and info[4] or None
            tel_phone=None
            email=None
            if not key:
                continue
            if key and key not in infomp:
                infomp[key]=[]
            infomp[key].append({
                'dictr':dictr,
                'address' : address,
                'phone' :str(phone),
                'tel_phone':tel_phone,
                'email':email
            })

        return infomp
    #验证是否为本人
    # 1.实名认证,绑定手机和申请手机号一致
    # 2.申请手机在淘宝收货地址手机中,次数最多
    # 3.姓名在淘宝收货人中
    def base_line(self,basedata):
        #绑定手机号是否一致
        bphone=basedata.tb and basedata.tb.bindMobile or u'unknown'
        own_phone = basedata.user_phone[:3]+'****'+basedata.user_phone[7:]
        same_phone = own_phone in bphone and 1 or 0
        #地址
        tb_address = basedata.tb and basedata.tb.addrs or []
        tb_addr_list = [{
            'host_name' : it[0],
            'dictr' : it[1],
            'address' : it[2],
            'phone' : it[4].replace('\t','').replace('\n',''),
            'tel_phone' : u'---',
            'email' : u'---'
        } for it in map(lambda x:x.replace('默认收货地址 : ','').split('|'),tb_address)]        
        tb_uphone=basedata.user_phone[:2]+'*******'+basedata.user_phone[9:] 
        mp={}
        for it in tb_addr_list:
            key = it['phone']
            if key not in mp:
                mp[key] = 0
            mp[key]+=1
        sort_up = mp and sorted(mp.items(),key=lambda s:s[1],reverse=True)[0][0] or 'None'
        phone_in_addr = tb_uphone in sort_up and 1 or 0
        count = same_phone+phone_in_addr
        if not count:
            basedata.tb=None
        pass


    def load_rule_data(self,basedata):

        self.min_rule_map={
            40001:self.binding_phone(basedata),#是否绑定手机
            40002:self.real_name(basedata),#实名认证
            40003:self.repay_back_fast(basedata),#淘宝急速退款金额
            40004:self.cat_level(basedata),#天猫等级
            40005:self.credit_grade(basedata),#淘宝信用等级
            40006:self.cat_grade(basedata),#天猫积分
            40007:self.profit_amount(basedata),#余额总收益
            40008:self.hb_amount(basedata),#花呗总额度
            40009:self.consume_times(basedata),#淘宝消费次数
            40010:self.cat_exep_value(basedata),#天猫经验值
            40011:self.bindp_same_with_owner_phone(basedata),#绑定手机号与申请号是否一致
            40012:self.safe_level(basedata),#账号安全级别
            40013:self.goods_nums_harf(basedata),#半年内成功交易的商品件数
            40014:self.max_min_amount_diff(basedata),#半年内单件商品最大消费金额与最小消费差值
            40015:self.consume_hz(basedata),#消费频次
            40016:self.using_year(basedata),#淘宝使用年限
            40017:self.close_order_times(basedata),#半年内关闭的订单数
        }

    #基本验证
    def is_basic(self,basedata,r):
        if not basedata.tb:
            r.feature_val = u'unknown'
            r.source = u'unknown'
            r.value = u'unknown'
            r.score = 10
            return r
    #是否绑定手机号
    def binding_phone(self,basedata):
        bphone=basedata.tb and basedata.tb.mobileVerified or u'unknown'
        r=minRule()
        r.name=u'是否绑定手机号'
        r.score =40
        if u'已绑定' in bphone:
            r.score = 100
        r.value=bphone
        r.feature_val = bphone
        r.source = bphone
        self.is_basic(basedata,r)
        return r
    
    #实名认证
    def real_name(self,basedata):
        rname = basedata.tb and basedata.tb.identityVerified or u'unknown'
        r=minRule()
        r.name=u'实名验证'
        r.score=20
        if u'已完成' in rname:
            r.score = 100
        r.value = rname
        r.feature_val = rname
        r.source = rname
        self.is_basic(basedata,r)
        return r
    #淘宝急速退款金额
    def repay_back_fast(self,basedata):
        rt_money=basedata.tb and basedata.tb.taobaoFastRefundMoney or -1
        r=minRule()
        r.name = u'淘宝急速退款金额'
        r.score = 10
        if rt_money>0 and rt_money<=1000:
            r.score = 100
        elif rt_money>1000 and rt_money<=2000:
            r.score=80
        elif rt_money>2000 and rt_money<=3000:
            r.score = 60
        elif rt_money>3000 and rt_money<=5000:
            r.score = 40
        elif rt_money>5000 and rt_money<=8000:
            r.score = 20
        r.value = str(rt_money)
        r.feature_val = str(rt_money)
        r.source = str(rt_money)
        self.is_basic(basedata,r)
        return r


    #天猫等级
    def cat_level(self,basedata):
        cat_grade=basedata.tb and basedata.tb.tianMaoLevel or u'unknown'
        r=minRule()
        r.name=u'天猫等级'
        r.score = 20
        if u'1'== cat_grade:
            r.score = 40
        elif u'2' == cat_grade:
            r.score = 60
        elif u'3' == cat_grade:
            r.score = 70
        elif u'4' == cat_grade:
            r.score = 90
        elif u'5' == cat_grade:
            r.score = 100
        r.value = cat_grade
        r.feature_val = cat_grade
        r.source = cat_grade
        self.is_basic(basedata,r)
        return r
    #淘宝信用等级
    def credit_grade(self,basedata):
        credit_level = basedata.tb and str(basedata.tb.creditLevel) or u'unknown'
        r=minRule()
        r.name = u'淘宝信用等级'
        r.score = 20
        if u'V0' in credit_level:
            r.score = 30
        elif u'V1' in credit_level:
            r.score = 50
        elif u'V2' in credit_level:
            r.score = 60
        elif u'V3' in credit_level:
            r.score = 70        
        elif u'V4' in credit_level:
            r.score = 80
        elif u'V5' in credit_level:
            r.score = 90
        elif u'V6' in credit_level:
            r.score = 100

        r.value = credit_level
        r.feature_val = credit_level
        r.source = credit_level
        self.is_basic(basedata,r)
        return r
    #天猫积分
    def cat_grade(self,basedata):
        ss = basedata.tb and basedata.tb.tianMaoPoints or u'unknown'
        score=ss.replace(u'积分','').replace(' ','')
        r=minRule()
        r.name=u'天猫积分'
        r.score = 10 
        if u'unknown' in str(score):
            r.score = 10
        elif score>0 and score<=200:
            r.score = 40
        elif score >200 and score<=300:
            r.score = 60
        elif score>300 and score<=500:
            r.score = 80
        elif score>500 and score<=700:     
            r.score = 100

        r.value = ss
        r.feature_val = ss
        r.source= ss
        self.is_basic(basedata,r)
        return r
    #余额总收益
    def profit_amount(self,basedata):
        pa = u'unknow'
        if basedata.tb:
            pa = float(basedata.tb.aliPaymFundProfit)
        r=minRule()
        r.name = u'余额宝总收益'
        r.score = 20
        if u'unknow' in str(pa):
            pass
        elif pa>0 and pa<=10:
            r.score = 40
        elif pa>10 and pa<=30:
            r.score = 60
        elif pa>30 and pa<=60:
            r.score = 80
        elif pa>60 and pa<=80:
            r.score = 90
        elif pa>80:
            r.score = 100
        r.value = str(pa)
        r.feature_val = str(pa)
        r.source = str(pa)    
        self.is_basic(basedata,r)
        return r

    #花呗总额度
    def hb_amount(self,basedata):
        hb=basedata.tb and basedata.tb.huabeiTotalAmount or -1
        r = minRule()
        r.name = u'花呗总额度'
        r.score = 10
        if hb<=1000:
            r.score = 30
        elif hb>1000 and hb<=2000:
            r.score = 50
        elif hb>2000 and hb<=3000:
            r.score = 60
        elif hb>3000 and hb<=4000:
            r.score = 70
        elif hb>4000 and hb<=5000:
            r.score = 80
        elif hb>5000:
            r.score = 100
        r.value = str(hb)
        r.feature_val = str(hb)
        r.source = str(hb)
        self.is_basic(basedata,r)
        return r         

    #天猫经验值
    def cat_exep_value(self,basedata):
        cat_exp= basedata.tb and int(basedata.tb.tianmaoExperience) or -1
        r = minRule()
        r.name = u'天猫经验值'
        r.score = 10
        if cat_exp<5000:
            r.score = 40
        elif cat_exp>=5000 and cat_exp<10000:
            r.score = 60
        elif cat_exp>=10000 and cat_exp<20000:
            r.score = 80
        else:
            r.score = 1000
        r.value = str(cat_exp)
        r.feature_val = str(cat_exp)
        r.source = str(cat_exp)
        self.is_basic(basedata,r)
        return r

    #淘宝消费次数
    def consume_times(self,basedata):
        order_len=len(self.harf_order_list)
        r = minRule()
        r.name = u'淘宝消费次数'
        r.score = 10
        if order_len>=0 and order_len<=10:
            r.score = 30
        elif order_len>10 and order_len<=30:
            r.score = 50
        elif order_len>30 and order_len<=50:
            r.score = 70
        elif order_len>50 and order_len<=70:
            r.score = 80
        elif order_len>70 and order_len<=100:
            r.score = 90
        else:
            r.score = 100
        r.value = str(order_len)
        r.feature_val = str(order_len)
        r.source = str(order_len)
        self.is_basic(basedata,r)
        return r

    #绑定手机号与申请号是否一致
    def bindp_same_with_owner_phone(self,basedata):
        bphone=basedata.tb and basedata.tb.bindMobile or u'unknown'
        r = minRule()
        r.name = u'绑定手机号与申请号是否一致'        
        r.score = 30
        own_phone = basedata.user_phone[:3]+'****'+basedata.user_phone[7:]
        if own_phone in bphone:
            r.score = 100
        r.value = bphone
        r.feature_val = bphone
        r.source = bphone
        self.is_basic(basedata,r)
        return r

    #收货地址是否与申请号手机归属地一样
    def addrs_in_plocation(self,basedata):
        pass
    #账号安全级别
    def safe_level(self,basedata):
        safe_level = basedata.tb and basedata.tb.safeLevel or u'unknown'
        r = minRule()
        r.name = u'账号安全级别'
        r.score = 10
        if u'高' in safe_level:
            r.score = 100
        elif u'中' in safe_level:
            r.score = 80
        elif u'低' in safe_level:
            r.score = 60
        r.value = safe_level
        r.feature_val = safe_level
        r.source = safe_level
        self.is_basic(basedata,r)
        return r
    #半年内购买商品件数
    def goods_nums_harf(self,basedata):
        order_list = self.harf_order_list
        count=0
        r = minRule()
        for it in order_list:
            if u'成功' in it['orderStatus']:
                count+=len(it['orderProducts'])
                r.value += '\t'.join([v[u'productName']+'-'+v[u'productPrice'] for v in it['orderProducts'] ])    

        r.name = u'半年内交易成功的商品件数'
        r.score = 10 
        if count>0 and count<10:
            r.score = 20
        elif count>10 and count<=40:
            r.score = 40
        elif count>40 and count<=70:
            r.score = 70
        elif count>70 and count<=100:
            r.score = 80
        elif count>100:
            r.score=100
        r.feature_val = str(count)
        r.source = str(count)
        self.is_basic(basedata,r)
        return r
    #半年内单件商品最大消费金额与最小消费差值
    def max_min_amount_diff(self,basedata):
        max_goods,min_goods='',''
        max_amount,min_amount=0,0
        order_list = self.harf_order_list
        for it in order_list:
            for itt in it['orderProducts']:
                money=float(itt['productPrice'])
                if money>max_amount:
                    max_amount=money
                    max_goods=itt['productName']+'-'+itt['productPrice']
                if money<min_amount:
                    min_amount=money
                    min_goods=itt['productName']+'-'+itt['productPrice']

        diff = max_amount-min_amount
        r=minRule()
        r.name = u'半年内单件商品最大消费金额与最小消费差值'
        r.value = max_goods+'\t'+min_goods
        r.score=10
        if diff>0 and diff<20:
            r.score = 30
        elif diff>=20 and diff<40:
            r.score = 50
        elif diff >= 40:
            r.score = 60
        r.feature_val=str(diff)
        r.source = str(diff)
        self.is_basic(basedata,r)
        return r

    #半年内关闭的订单数
    def close_order_times(self,basedata):
        order_list = self.harf_order_list
        corder_list =[ it for it in order_list if u'关闭' in it['orderStatus']]
        times=len(corder_list)

        r = minRule()
        r.name = u'半年内关闭的订单数'
        r.value = '\t'.join([ it['orderId']+'-'+ it['orderTotalPrice']+'-'+ it['businessDate']  for it in corder_list])
        r.score = 10
        times=len(corder_list)
        if corder_list:
            if times>=0 and times<=10:
                r.score = 100
            elif times>10 and times<=20:
                r.score = 80
            elif times>20 and times<=40:
                r.score = 60
            elif times>40:
                r.score = 30
        r.feature_val = str(times)
        r.source = str(times)
        self.is_basic(basedata,r)
        return r



    #半年内购买单件商品金额众数
    def most_times_amount(self,basedata):
        pass
    #半年内消费频次
    def consume_hz(self,basedata):
        order_list = self.harf_order_list
        count = 0
        r=minRule()
        for it in order_list:
            count +=len(it['orderProducts'])
        avg=count/6

        r=minRule()
        r.name = u'半年内消费频次'
        r.score = 10
        if avg<5:
            r.score = 40
        elif avg>=5 and avg<10:
            r.score = 70
        elif avg>=10 and avg<15:
            r.score = 80
        elif avg>=15:
            r.score = 100
        r.feature_val = str(avg)
        r.source = str(avg)
        self.is_basic(basedata,r)
        return r
    #淘宝使用年限
    def using_year(self,basedata):
        order_list=basedata.tb and basedata.tb.orderList or []
        now=basedata.create_time
        min_dt=now
        value=''
        for o in order_list:
            dt=o['businessDate'].split('-')
            d=datetime(int(dt[0]),int(dt[1]),int(dt[2]))
            if d<min_dt:
                min_dt = d
                value = o['businessDate']

        y=(now-min_dt).days/365
        r = minRule()
        r.name = u'淘宝使用年限'
        if y<1:
            r.score = 10
        elif y>=1 and y<3:
            r.score = 40
        elif y>=3 and y<5:
            r.score = 80
        elif y>=5:
            r.score = 100
        r.value = value
        r.feature_val = str(y)
        r.source = str(y)
        self.is_basic(basedata,r)
        return r

    def get_score(self):
        min_map = self.min_rule_map 

        binding_phone = min_map[40001].score*0.03 #是否绑定手机
        real_name = min_map[40002].score*0.07 #实名认证
        repay_back_fast = min_map[40003].score*0.05 #淘宝急速退款金额
        cat_level = min_map[40004].score*0.05 #天猫等级
        credit_grade = min_map[40005].score*0.1 #淘宝信用等级
        cat_grade = min_map[40006].score*0.05 #天猫积分
        profit_amount = min_map[40007].score*0.1 #余额总收益
        hb_amount = min_map[40008].score*0.1 #花呗总额度
        consume_times = min_map[40009].score*0.1 #淘宝消费次数
        cat_exep_value = min_map[40010].score*0.05  #天猫经验值
        bindp_same_with_owner_phone = min_map[40011].score*0.02 #绑定手机号与申请号是否一致
        safe_level = min_map[40012].score*0.03 #账号安全级别
        goods_nums_harf = min_map[40013].score*0.05 #半年内购买商品件数
        max_min_amount_diff = min_map[40014].score*0.06 #半年内单件商品最大消费金额与最小消费差值
        consume_hz = min_map[40015].score*0.05 #消费频次
        using_year = min_map[40016].score*0.05 #淘宝使用年限
        close_times = min_map[40017].score*0.04

        score = binding_phone+real_name+repay_back_fast+cat_level
        score += credit_grade+cat_grade+profit_amount+hb_amount+consume_times
        score += cat_exep_value + bindp_same_with_owner_phone+safe_level
        score += goods_nums_harf+max_min_amount_diff+consume_hz+using_year+close_times
        
        return score

