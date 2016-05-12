#!/usr/bin/env python
# encoding: utf-8
import sys
import os
reload(sys)
import json
import re
from datetime import datetime,timedelta
sys.setdefaultencoding('utf8')
from django.conf import settings
from rules.raw_data import minRule
from rules.models import BaseRule
from rules.base import get_right_datetime

class Sp(BaseRule):

    def __init__(self,basedata):
        self.recharge_map = self.init_recharge_map(basedata)
        self.call_record_map = self.init_phone_record_mp(basedata)
        self.sms_record_map = self.init_sms_record_mp(basedata)
        #催收
        self.dunning_map=self.init_cuishou_map()
       
        self.min_rule_map={
            20001:None,#半年内充值金额
            20002:None,#半年内充值次数
            20003:None,#半年内平均充值间隔(天/次)
            20004:None,#半年内主叫次数
            20005:None,#半年内被叫次数
            20006:None,#通话记录电话号码出现在通讯录的比例
            20007:None,#短信记录电话号码出现在通讯录中的比例
            20008:None,#通话记录电话号码在老家的比例
            20009:None,#短信记录电话号码在老家的比例
            20010:None,#通话记录中电话号码与申请人同一手机归属地的比例
            20011:None,#短信记录中电话号码与申请人同一手机归属地的比例
            20012:None,#是否设置21呼叫转移
            20013:None,#是否电话被催收
            20014:None,#是否被短信催收
            20015:None,#手机所在地在上网地点出现次数
            20016:None,#与021,0755通话次数
            20017:None,#申请号与本机有通话
            20018:None,#是否停机过
        }

    def init_cuishou_map(self):
        ppmap = {}
        f1 = settings.CUISHOU_GUHUA_FILE
        f2 = settings.CUISHOU_SHOUJI_FILE
        for line in open(f1,'r'):
            l = line.strip().split('\t')
            ppmap[l[0]]= l[1]
        for line in open(f2,'r'):
            l = line.strip().split('\t')
            ppmap[l[0]]= l[1]
        return ppmap

    def init_recharge_map(self,basedata):
        mp=json.loads(basedata.sp.recharge)['data']
        charge_mp={}
        now=basedata.create_time
        for it in mp:
            td=it['payDate']
            key=datetime(int(td[0:4]),int(td[4:6]),int(td[6:8]),int(td[8:10]),int(td[10:12]),int(td[12:14]))
            if key>now-timedelta(180) and key<=now:
                charge_mp.update({
                    key:it['payFee']
                })
        return charge_mp

    #通话记录
    def init_phone_record_mp(self,basedata):
        cmp={}
        for call in basedata.sp_calls:
            if call.phone not in cmp:
                print call.phone_location
                cmp[call.phone]=call.phone_location
        return cmp
    #短信记录
    def init_sms_record_mp(self,basedata):
        smsmap={}
        for sms in basedata.sp_sms:
            if sms.phone not in smsmap:
                smsmap[sms.phone] = sms.phone_location
        return smsmap

    '''半年内充值金额'''
    def get_incharge_amount_harf_year(self):
        r=minRule()
        r.value=''
        r.score =0
        re_map=self.recharge_map
        amount = 0
        for k,v in re_map.items():
            amount+=float(v)
            r.value+='\n时间:'+str(k)+'; 金额:'+v+'元'
        r.value = '\t'.join([ '时间:'+str(k)+'; '+str(v) for k,v in re_map.items() ])
        r.name='半年内充值金额:'+str(amount)
        if amount<=30:
            r.score=10
        elif amount>30 and amount<100:
            r.score=50
        elif amount>=100:
            r.amount=100
        r.source = str(amount)
        return r

    '''半年内充值次数'''
    def get_incharge_times_harf_year(self):
        r=minRule()
        r.value=''
        r.score =0
        re_map=self.recharge_map
        times=len(re_map.keys())
        r.value='\t'.join([ '时间:'+str(k)+'; '+'1次' for k,v in re_map.items() ])
        r.name='半年内充值次数:'+str(times)
        if times<=30:
            r.score=10
        elif times>30 and times<100:
            r.score=50
        elif tiems>=100:
            r.amount=100
        r.source = str(times)
        return r

    '''半年内平均每隔多少天充值一次'''
    def get_incharge_inter_days(self):
        r=minRule()
        r.value=u'30'
        r.name=u'充值话费的平均时间间隔'
        r.score=0
        re_list=self.recharge_map.keys()
        re_list.sort()
        days=0
        for i in range(0,len(re_list)-1):
            v=re_list[i]
            v_next=re_list[i+1]
            days+=(v_next-v).days
        avg=days/(len(re_list) or 1)
        r.value='\t'.join([ '登陆时间:'+str(it) for it in re_list])
        r.name=u'半年内平均充值间隔'+str(avg)
        if avg>0 and avg<5:
            r.score=100
        elif avg>=5 and avg<10:
            r.score=80
        elif avg>=10 and avg<15:
            r.score=60
        elif avg>=15:
            r.score=0
        r.source = str(avg)
        return r

    '''主叫次数'''
    def get_call_in_times(self,basedata):
        times=0
        for call in basedata.sp_calls:
            if call.call_type == u'主叫':
                times+=1
        r = minRule()
        r.name='主叫次数'
        r.score=0
        r.source = str(times)
        return r

   
    '''主叫时长'''
    def get_call_in_duration(self,basedata):
        duration=0
        for call in basedata.sp_calls:
            if call.call_type == u'主叫':
                duration+=call.call_duration
        r = minRule()
        r.name='主叫时长'
        r.score=0
        r.source=str(duration)
        return r
    '''被叫次数'''
    def get_call_out_times(self,basedata):
        times=0
        for call in basedata.sp_calls:
            if call.call_type == u'被叫':
                times+=1
        r = minRule()
        r.name='被叫次数'
        r.score=0
        r.source=str(times)
        if times<1000:
            r.score=20
        elif times>=1000 and times<3000:
            r.score=30
        elif times>=3000 and times<4000:
            r.score=40
        return r
    '''被叫时长'''
    def get_call_out_duration(self,basedata):
        duration=0
        for call in basedata.sp_calls:
            if call.call_type == u'被叫':
                duration+=call.call_duration

        r = minRule()
        avg=duration
        r.name='被叫时长'
        r.score=0
        r.source=str(avg)
        if avg<1000:
            r.score=20
        elif avg>=1000 and avg<3000:
            r.score=30
        elif avg>=3000 and avg<4000:
            r.score=40    
        return r


    '''通话记录电话号码出现在通讯录的比例'''
    def callsame_location_with_contact(self,basedata):
        contact = basedata.good_contacts
        count=0
        for it in contact:
            if it.phone in self.call_record_map:
                count+=1
    '''短信记录电话号码出现在通讯录中的比例'''
    def smssame_location_with_contact(self,basedata):
        contact=basedata.good_contacts
        count=0
        for it in contact:
            if it.phone in self.sms_record_map:
                count+=1

    '''通话记录中电话号码在老家的比例'''
    def callsame_location_with_idcard(self,basedata):
        home_location = basedata.home_location
        count=0
        for k,v in self.call_record_map.items():
            location=v.split('-')
            '''级别:省,市/县'''
            if location[0] in home_location or location[1] in home_location:
                count+=1 
                print k,v,home_location

    '''短信记录电话号码在老家的比例'''
    def smssame_location_with_idcard(self,basedata):
        home_location = basedata.home_location
        count=0
        for k,v in self.sms_record_map.items():
            location=v.split('-')
            '''级别:省,市/县'''
            if location[0] in home_location or location[1] in home_location:
                count+=1
                print k,v,home_location

    '''通话记录中电话号码与申请人同一手机归属地的比例'''
    def callsame_location_with_userphone(self,basedata):
        user_plocation = basedata.user_plocation
        count=0
        for k,v in self.call_record_map.items():
            location=v.split('-')
            if location[1] in user_plocation or location[0] in user_plocation:
                count+=1
                print k,v,user_plocation

    '''短信记录中电话号码与申请人同一手机归属地的比例'''
    def smssame_location_with_userphone(self,basedata):
        user_plocation = basedata.user_plocation
        count=0
        for k,v in self.sms_record_map.items():
            location=v.split('-')
            print v
            if location[1] in user_plocation or location[0] in user_plocation:
                count+=1
                print k,v,user_plocation

    '''是否设置21呼叫转移'''
    def set_21(self,basedata):
        r=minRule()
        r.name='是否设置21呼叫转移'
        r.score=0
        for c in basedata.contacts:
            if c.phone[0:2] =='21' or c.phone[0:3] =='*21' or c.phone[0:3]=='#21':
                return r
        r.score=1
        return r 

    '''是否电话被催收'''
    def is_dunning_call(self,basedata):
        r=minRule()
        r.name=u'是否被催收'
        r.score=0
        for k,v in self.call_record_map.items():
            if k in self.dunning_map:
                return r
        r.score=1
        return r

    '''是否被短信催收'''
    def is_dunning_sms(self,basedata):
        r=minRule()
        r.name=u'是否被催收'
        r.score=0
        for k,v in self.sms_record_map.items():
            if k in self.dunning_map:
                return r
        r.score=1
        return r

    '''手机归属地与上网所在地一致'''
    def phone_location_int_net_location(self,basedata):
        net_map={}
        user_plocation=basedata.user_plocation
        r=minRule()
        user_plocation=basedata.user_plocation
        for net in basedata.sp_net:
            if net.net_location not in net_map:
                net_map[net.net_location]=''
        if user_plocation not in net_map:
            r.score=0
        r.score=1
        return r
    '''与021,0755通话次数'''
    def call_with_021_0755(self,basedata):
        resmap={}
        for call in basedata.sp_calls:
            try:
                kk=None
                phone=call.phone
                datastr='通话开始时间:'+str(call.calling_time)+';通话时长:'+str(call.calling_duration)+'s;'
                datastr+='号码:'+phone+';'+phone_type[call.type]+';信息来源:'+call.source
                if u'021' in phone[0:3]:
                    kk=phone[0:7]+'xxxx'
                elif u'0755' in phone[0:4]:
                    kk=phone[0:8]+'xxxx'
                if kk:
                    if kk not in resmap:
                        resmap[kk]=[datastr]
                    else:
                        resmap[kk].append(datastr)
            except:
                continue
        if resmap:
            print 'hava'
    '''申请号与本机有通话'''
    def userphone_in_calls_or_sms(self,basedata):
        user_phone=basedata.user_phone
        if user_phone in self.sms_record_map or user_phone in self.sms_record_map:
            return 100
        return 0        

    '''
    def incharge_money_in_month(self):
        r=minRule()
        r.value=''
        r.score =0
        re_map=self.recharge_map
        amount,times=0,0
        for k,v in re_map.items():
            amount+=float(v)
            times+=1
            r.value+='\n时间:'+str(k)+'; 金额:'+v+'元'
        avg=amount*1.0/(times or times+1)
        r.name='历史平均充值金额(充值金额/充值次数):次数：'+str(times)+';金额:'+str(amount) 
        if avg<=30:
            r.score=10
        elif avg>30 and avg<100:
            r.score=50
        elif avg>=100:
            r.score=100
        r.source='{"times":%s,"money":%s}'%(str(times),str(amount))
        return r

    def call_times_out_his(self):
        r=minRule()
        r.value=''
        r.name='历史通话主叫次数'
        r.score=0
        phone_map=self.phone_map
        count=0
        duration=0
        for k,v in phone_map.items():
            for vv in v:
                if vv['commMode']==u'主叫':
                    count+=1
                    d = vv['commTime'].replace('分',' ').replace('秒','').split(' ')
                    minu = len(d)>1 and int(d[0])*60 or 0
                    sec = len(d)>1 and int(d[1]) or int(d[0])
                    duration+=(minu+sec)
        avg=duration/(count or 1)
        if avg<1000:
            r.score=20
        elif avg>=1000 and avg<3000:
            r.score=30
        elif avg>=3000 and avg<4000:
            r.score=40
        r.value=str(avg)
        r.name='历史通话主叫时长/次数:'+str(count)+';时间:'+str(duration)+'s'
        r.source='{"times":%s,"duration":%s}'%(str(count),str(duration))        
        return r

    def call_times_in_his(self):
        r=minRule()
        r.score=30
        r.name='历史通话被叫次数'
        phone_map=self.phone_map
        count=0
        duration=0
        for k,v in phone_map.items():
            for vv in v:
                if vv['commMode']==u'被叫':
                    count+=1
                    d = vv['commTime'].replace('分',' ').replace('秒','').split(' ')
                    minu = len(d)>1 and int(d[0])*60 or 0
                    sec = len(d)>1 and int(d[1]) or int(d[0])
                    duration+=(minu+sec)
        avg=duration/(count or 1)
        if avg<1000:
            r.score=20
        elif avg>=1000 and avg<3000:
            r.score=30
        elif avg>=3000 and avg<4000:
            r.score=40
        r.value=str(avg)
        r.name='历史通话被叫时长/次数:'+str(count)+';时间:'+str(duration)+'s'
        r.source='{"times":%s,"duration":%s}'%(str(count),str(duration))      
        return r

    def incharge_interdays(self):
        r=minRule()
        r.value=u'30'
        r.name=u'充值话费的平均时间间隔'
        r.score=0
        re_list=self.recharge_map.keys()
        re_list.sort()
        days=0
        for i in range(0,len(re_list)-1):
            v=re_list[i]
            v_next=re_list[i+1]
            days+=(v_next-v).days
        avg=days/(len(re_list) or 1)
        r.name=u'充值话费的平均时间间隔:'+str(avg)
        r.source = '{"days":%s,"times":%s}'%(str(days),str(len(re_list)))
        return r
    def name_in_contact(self):
        r=minRule()
        r.value='30'
        r.name=u'运营商联系人与通讯录联系人匹配个数'
        r.value=u'30'
        r.source = str(30)
        return r
    '''

    def get_score(self):
        min_rule_map = self.min_rule_map
        incharge_money_score=min_rule_map[30001].score*0.2
        call_time_money_score=min_rule_map[30002].score*0.2
        call_time__in_score=min_rule_map[30003].score*0.2
        name_in_contact_score=min_rule_map[30005].score*0.2
        incharge_interdays=min_rule_map[30004].score*0.2
        score=incharge_money_score+call_time_money_score+call_time__in_score+name_in_contact_score+incharge_interdays
        return score
