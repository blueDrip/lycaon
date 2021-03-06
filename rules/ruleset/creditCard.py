#!/usr/bin/env python
# encoding: utf-8
import sys
import os
reload(sys)
from django.conf import settings
from datetime import datetime,timedelta
from rules.models import BaseRule
from rules.raw_data import minRule

class creditCard(BaseRule):
    def __init__(self,basedata):

        self.cm_detail_list = []
        self.city_map = self.init_city_map()

    #判断是否本人申请
    def base_line(self,basedata):
        self.chef_map={}
        pass 
    def load_rule_data(self,basedata):
        self.init_cmbcc(basedata)        
        self.min_rule_map={
            60001:self.get_all_credit_amount(basedata),#信用额度
            60002:self.get_can_user_credit_amount_current(basedata),#当前可用信用额度
            60003:self.get_repay_amount_before_3month(basedata),#近三个月内信用卡月还款金额
            60004:self.get_avg_amount_by_month(basedata),#三个月内月刷卡金额
            60005:self.get_times_of_thress_month(basedata),#三个月内刷卡频次
            60006:self.credit_card_location(basedata),#持卡人所在地去都市化程度
            60007:self.get_most_amount_times(basedata),#三个月内消费金额>=8000元次数
            60008:self.company_address_same_with_phone_location(basedata),#公司所在地址是否与手机归属地一致
        }


    #基本验证
    def is_basic(self,basedata,r):
        if not basedata.cb:
            r.feature_val = u'unknow'
            r.source = u'unknow'
            r.value = u'unknow'
            r.score = 10
            return r



    def init_cmbcc(self,basedata):
        cb_detail_map = basedata.cb and basedata.cb.detailBill or {}
        now = basedata.create_time
        for k,v in cb_detail_map.items():
            date_year = k.split('_')[1][:4]
            for it in v:
                date = it['business_day'].replace("'",'').split('-')
                date_month=date[0]
                date_day = date[1]
                time = datetime(int(date_year),int(date_month),int(date_day))
                if time>now-timedelta(90) and time<now:
                    self.cm_detail_list.append({
                        'business_day':time,
                        'business_money': float(it['business_money'].replace(u"'￥",'').replace(',','')),
                        'business_customer':it['business_customer'],
                    })
        
    def init_city_map(self):
        f = open(settings.CITY_CONF,'r')
        lines = f.readlines()
        f.close()
        city_map={}
        for line in lines:
            str_list = line.replace('\n','').decode('utf-8').split('\t')
            k = str_list[0]
            v = str_list[1]
            if k not in city_map:
                city_map[k]=[]
            city_map[k].append(v)
        return city_map

	#'''profession'''
    #def get_profession(self,basedata):
    #    r = minRule()
    #    r.name = u'职业'
    #    r.value = u'老师'
    #    r.score =0
    #    r.source = u'老师'
    #    r.feature_val = r.source
    #    return r
    '''当前信用额度'''
    def get_all_credit_amount(self,basedata):
        amount = basedata.cb and basedata.cb.totalAmount or u'unknow'
        r = minRule()
        r.name = u'当前信用额度'
        r.value = u'当前额度:'+amount
        amount_float = amount !=u'unknow' and float(amount.replace(',','').replace(u'￥','')) or amount
        if amount_float == u'unknow':
            r.score  = 0
        elif amount_float <=10000:
            r.score = 30
        elif amount_float >=10000 and amount_float<20000:
            r.score = 50
        elif amount_float>=20000 and amount_float<30000:
            r.score = 70
        elif amount_float>=30000 and amount_float<40000:
            r.score = 90
        elif amount_float>=40000:
            r.score = 100
        else:
            r.score = 10
        r.feature_val = u'额度:'+amount
        r.source = str(amount_float)
        self.is_basic(basedata,r)
        return r

    '''当前可用额度'''
    def get_can_user_credit_amount_current(self,basedata):
        can_use_amount = basedata.cb and basedata.cb.canUserAmount or u'unknow'
        r = minRule()
        r.name = u'当前可用额度'
        r.value = u'当前可用额度:'+can_use_amount
        amount_float = can_use_amount != u'unknow' and float(can_use_amount.replace(',','').replace(u'￥','')) or can_use_amount
        if amount_float == u'unknow':
            r.score = 0
        elif amount_float <=10000:
            r.score = 30
        elif amount_float >=10000 and amount_float<20000:
            r.score = 50
        elif amount_float>=20000 and amount_float<30000:
            r.score = 70
        elif amount_float>=30000 and amount_float<40000:
            r.score = 90
        elif amount_float>=40000:
            r.score = 100
        else:
            r.score = 10
        r.feature_val = u'额度:'+can_use_amount
        r.source = str(amount_float)
        self.is_basic(basedata,r)
        return r

    '''近三个月内信用卡月还款金额'''
    def get_repay_amount_before_3month(self,basedata):
        bill_map = basedata.cb and basedata.cb.simpleBill or {}
        now = basedata.create_time
        r_amount=0
        value=[]
        for k,v in bill_map.items():
            amount=v.replace(u'￥','').replace(',','')
            kk = k.split('-')
            repay_date = datetime(int(kk[0]),int(kk[1]),1)
            
            if repay_date>=now-timedelta(90) and repay_date<=now:
                r_amount+=float(amount)       
                value.append(u'日期:'+k+u' ; 金额'+v)

        r = minRule()
        r.name = u'近三个月内信用卡月还款金额'
        r.value ='\t'.join([ it for it in value ])
        r.score = 0
        avg_amount=r_amount/3.0
        if avg_amount<10000:
            r.score = 40
        elif avg_amount>=10000 and avg_amount<15000:
            r.score = 60
        elif avg_amount>=15000 and avg_amount<20000:
            r.score = 80
        elif avg_amount>=20000 and avg_amount<25000:
            r.score = 90
        elif avg_amount>=25000:
            r.score = 100
        r.feature_val = '月还款金额:'+'%.2f'%(avg_amount)
        r.source = str(r_amount)
        self.is_basic(basedata,r)
        return r
    '''三个月内月刷卡金额'''
    def get_avg_amount_by_month(self,basedata):
        cm_list = self.cm_detail_list
        amount = 0
        value = []
        for cm in cm_list:
            amount += cm['business_money']
            
        r = minRule()
        r.score = 0
        r.name = u'三个月内月刷卡金额'
        r.feature_val = u'月刷卡金额:￥-%s'%('%.2f'%(amount/3.0))
        r.source = str(amount)
        r.value='\t'.join([ u'时间:'+str(it['business_day'])+'; 金额：'+str(it['business_money'])+';'+it['business_customer'] for it in cm_list])
        avg_amount=amount/3.0
        if avg_amount<1000:
            r.score = 20
        elif avg_amount>=1000 and avg_amount<2000:
            r.score = 40

        elif avg_amount>=2000 and avg_amount<3000:
            r.score = 50
        else:
            r.score = 100
        self.is_basic(basedata,r)
        return r

    '''三个月内刷卡频次'''
    def get_times_of_thress_month(self,basedata):
        cm_list = self.cm_detail_list
        times = len(cm_list)
        r = minRule()
        r.name = u'三个月内刷卡频次'
        avg_times = times>=3 and times/3 or  1
        r.feature_val = u'频次:'+str(avg_times) +u'次'
        r.score =10
        if avg_times<100:
            r.score = 40
        elif avg_times>=100 and avg_times<200:
            r.score = 60
        elif avg_times>=200 and avg_times<300:
            r.score = 80
        elif avg_times>=300:
            r.score = 100
        r.value = u'暂不显示'
        r.source = str(times)
        self.is_basic(basedata,r)
        return r

    #'''是否逾期记录（还款>30天）'''
    #def get_repay_money_overdue_3month(self,basedata):
    #    r = minRule()
    #    r.name = u'是否逾期记录（还款>30天）'
    #    r.score = 0
    #    r.source = u'无'
    #    r.value = ''
    #    r.feature_val = '无'
    #    return r

    '''持卡人所在地区都市化程度'''
    def credit_card_location(self,basedata):
        bill_addr = basedata.cb and basedata.cb.billAddr.replace('\r\n','').replace(' ','') or u'unknow'
        flag=''
        for k,v in self.city_map.items():
            for it in v:
                if it in bill_addr:
                    flag=k
                    break;
           
        r = minRule()
        r.name = u'持卡人所在地区都市化程度'
        if u'一线城市' == flag:
            r.score = 100
        elif u'二线发达城市' == flag:
            r.score = 80
        elif u'二线中等发达城市' == flag:
            r.score = 70
        elif u'三线城市' == flag:
            r.score = 50
        elif u'四线城市' == flag:
            r.score = 40
        elif u'五线城市' == flag:
            r.score = 20
        else:
            r.score=10
        r.value=flag+';'+bill_addr
        r.source=flag
        r.feature_val = flag or u'其他'
        self.is_basic(basedata,r)
        return r

    '''三个月内单笔消费金额>=8000元的次数'''
    def get_most_amount_times(self,basedata):
        max_list=[]
        cm_list = self.cm_detail_list
        for cm in cm_list:
            if cm['business_money']>=8000:
                max_list.append(cm)
        
        mx_times = len(max_list)
        r = minRule()
        r.name = u'三个月内单笔消费金额>=8000元的次数'
        r.value = '\t'.join([ u'时间:'+str(it['business_day'])+ u'; 金额：'+str(it['business_money'])+';'+it['business_customer'] for it in max_list])

        if mx_times<=0:
            r.score=0
        else:
            r.score = mx_times<=10 and mx_times*10 or 100
        r.feature_val = u'次数:'+str(mx_times)
        r.source = str(mx_times)
        self.is_basic(basedata,r)
        return r

    '''公司所在地址是否与手机归属地一致'''
    def company_address_same_with_phone_location(self,basedata):
        user_pl = basedata.user_plocation
        bill_addr = basedata.cb and basedata.cb.billAddr.replace('\r\n','').replace(' ','') or u'---'
        r = minRule()
        r.name = u'公司所在地址是否与手机归属地一致'
        r.value = bill_addr
        r.source = u'unknown'
        r.score = 10
        if user_pl not in bill_addr:
            r.source = u'否'
            r.score = 10
        elif user_pl in bill_addr:
            r.source = u'是'
            r.score = 100
        else:
            r.score = 10
            r.source = u'unknow'

        r.feature_val = r.source
        self.is_basic(basedata,r)
        return r

    def get_score(self):
        min_map=self.min_rule_map
        all_credit_amount_score = min_map[60001].score*0.2 #信用额度
        amount_current = min_map[60002].score*0.2 #当前可用信用额度
        repay_amount = min_map[60003].score*0.1 #近三个月内信用卡月还款金额
        avg_amount = min_map[60004].score*0.1 #三个月内月刷卡金额
        avg_times = min_map[60005].score*0.1  #三个月内刷卡频次
        credit_card_location = min_map[60006].score*0.1 #持卡人所在地去都市化程度
        most_amount_time = min_map[60007].score*0.1 #三个月内消费金额>=8000元次数
        address_same = min_map[60008].score*0.1 #公司所在地址是否与手机归属地一致

        score = all_credit_amount_score + amount_current
        score += repay_amount + avg_amount + avg_times
        score += credit_card_location + most_amount_time + address_same
        return score
