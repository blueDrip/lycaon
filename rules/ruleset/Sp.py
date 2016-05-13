#!/usr/bin/env python
# encoding: utf-8
import sys
import os
reload(sys)
import json
import re
from datetime import datetime,timedelta
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
            20001:self.call_record_len(),#通话记录长度是否合理
            20002:self.sms_record_len(),#短信记录长度是否合理            
            20003:self.get_incharge_amount_harf_year(),#半年内充值金额
            20004:self.get_incharge_times_harf_year(),#半年内充值次数
            20005:self.get_incharge_inter_days(),#半年内平均充值间隔(天/次)
            20006:self.get_call_in_times(basedata),#半年内主叫次数
            20007:self.get_call_in_duration(basedata),#半年内主叫时长
            20008:self.get_call_out_times(basedata),#半年内被叫次数
            20009:self.get_call_out_duration(basedata),#半年内被叫时长
            20010:self.callsame_location_with_contact(basedata),#通话记录电话号码出现在通讯录的比例
            20011:self.smssame_location_with_contact(basedata),#短信记录电话号码出现在通讯录中的比例
            20012:self.callsame_location_with_idcard(basedata),#通话记录电话号码在老家的比例
            20013:self.smssame_location_with_idcard(basedata),#短信记录电话号码在老家的比例
            20014:self.callsame_location_with_userphone(basedata),#通话记录中电话号码与申请人同一手机归属地的比例
            20015:self.smssame_location_with_userphone(basedata),#短信记录中电话号码与申请人同一手机归属地的比例
            20016:self.set_21(basedata),#是否设置21呼叫转移
            20017:self.is_dunning_call(),#是否电话被催收
            20018:self.is_dunning_sms(),#是否被短信催收
            20019:self.phone_location_int_net_location(basedata),#手机所在地在上网地点出现次数
            20020:self.call_with_021_0755(basedata),#与021,0755通话次数
            20021:self.userphone_in_calls_or_sms(basedata),#申请号与本机有通话
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

    #半年内通话记录
    def init_phone_record_mp(self,basedata):
        cmp={}
        now=basedata.create_time
        for call in basedata.sp_calls:
            if call.call_time>now-timedelta(180) and call.call_time<=now:
                if call.phone not in cmp:
                    cmp[call.phone]=call.phone_location
        return cmp
    #半年内短信记录
    def init_sms_record_mp(self,basedata):
        smsmap={}
        now = basedata.create_time
        for sms in basedata.sp_sms:
            if sms.send_time>now-timedelta(180) and sms.send_time<=now:
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
        r.value = '\t'.join([ '时间:'+str(k)+'; '+str(v) for k,v in re_map.items() ])
        r.name='半年内充值金额'
        r.feature_val = '充值金额:'+str(amount)+'元'
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
        r.name='半年内充值次数'
        r.feature_val = '充值次数:'+str(times)+'次'
        if times<=30:
            r.score=10
        elif times>30 and times<100:
            r.score=50
        elif times>=100:
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
        r.value='\t'.join(['登陆时间:'+str(it) for it in re_list])
        r.name=u'半年内平均充值间隔'+str(avg)
        r.feature_val=str(avg)+'天/次'
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
        if times>=0 and times<10:
            r.score=10
        elif times>10 and times<=20:
            r.score = 20
        elif times>20 and times<=30:
            r.score = 30
        elif times>30 and times<=50:
            r.score = 50
        elif times>50:
            r.score=100
        r.name='主叫次数'
        r.value=str(times)
        r.source = str(times)
        r.feature_val = str(times)+'次'
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
        if duration>0 and duration<=500:
            r.score=20
        elif duration>500 and duration<=1000:
            r.score=30
        elif duration>1000 and duration<=2000:
            r.score=40
        elif duration>2000 and duration<=5000:
            r.score=60
        elif duration>5000 and duration<=10000:
            r.score=80
        elif duration>10000:
            r.score=100
        r.value = str(duration)
        r.feature_val = str(duration)+'s'
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
        r.source=str(times)
        r.value = str(times)
        r.feature_val = str(times)+'次'
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
        elif avg>=4000:
            r.score=100
        r.value = str(avg)
        r.feature_val = str(duration)+'s'
        return r

    '''通话记录电话号码出现在通讯录的比例'''
    def callsame_location_with_contact(self,basedata):
        contact = basedata.contacts
        value,count=[],0
        conlen = len(contact)
        for it in contact:
            if it.phone in self.call_record_map:
                count+=1
                value.append(
                    it.name+';'+it.phone+';'+it.phone_location
                )
        radio=count*1.0/(len(contact) or 1)
        r = minRule()
        r.name = '通话记录电话号码出现在通讯录的比例'
        r.value = '\t'.join(value)
        if radio>0 and radio<=1:
            r.score = radio*100
        elif radio>1:
            r.score = 100
        r.source = '{"count":%s,"conlen":%s}'%(str(count),str(conlen))
        r.feature_val = "%.2f"%(radio)
        return r


    '''短信记录电话号码出现在通讯录中的比例'''
    def smssame_location_with_contact(self,basedata):
        contact=basedata.contacts
        value,count=[],0
        conlen = len(contact)
        for it in contact:
            if it.phone in self.sms_record_map:
                count+=1
                value.append(
                    it.name+';'+it.phone+';'+it.phone_location
                )
        radio = count*1/(conlen or 1)
        r = minRule()
        r.name = '短信记录电话号码出现在通讯录的比例'
        if radio>0 and radio<=1:
            r.score = radio*100
        elif radio>1:
            r.score = 100
        r.value = '\t'.join(value)
        r.feature_val = "%.2f"%(radio)
        r.source = '{"count":%s,"conlen":%s}'%(str(count),str(conlen))
        return r

    '''通话记录中电话号码在老家的比例'''
    def callsame_location_with_idcard(self,basedata):
        home_location = basedata.home_location
        count=0
        value = ''
        for k,v in self.call_record_map.items():
            location=v.split('-')
            '''级别:省,市/县'''
            if location[0] in home_location or location[1] in home_location:
                count+=1 
                value+=k+';'+v+'\t'

        call_len = len(self.call_record_map.keys())
        radio = count*1.0/(call_len or 1)
        r = minRule()
        r.name = '通话记录中电话号码在老家的比例'
        r.value = value

        if radio>0 and radio<=0.1:
            r.score = 100
        elif radio>0.1 and radio<=1:
            r.score = radio*100
        elif radio>1:
            r.score = 50
        r.source = '{"count":%s,"conlen":%s}'%(str(count),str(call_len))
        r.feature_val = "%.2f"%(radio)
        return r


    '''短信记录电话号码在老家的比例'''
    def smssame_location_with_idcard(self,basedata):
        home_location = basedata.home_location
        count=0
        value = ''
        for k,v in self.sms_record_map.items():
            location=v.split('-')
            '''级别:省,市/县'''
            if location[0] in home_location or location[1] in home_location:
                count+=1
                value+=k+';'+v+'\t'
        sms_len = len(self.sms_record_map.keys())
        radio = count*1.0/(sms_len or 1)
        r = minRule()
        r.name = '通话记录中电话号码在老家的比例'
        r.value = value
        if radio>0 and radio<=0.1:
            r.score = 100
        elif radio>0.1 and radio<=1:
            r.score = radio*100
        elif radio>1:
            r.score = 50
        r.source = '{"count":%s,"smslen":%s}'%(str(count),str(sms_len))
        r.feature_val = "%.2f"%(radio)
        return r


    '''通话记录中电话号码与申请人同一手机归属地的比例'''
    def callsame_location_with_userphone(self,basedata):
        user_plocation = basedata.user_plocation
        count=0
        value = ''
        for k,v in self.call_record_map.items():
            location=v.split('-')
            if location[1] in user_plocation or location[0] in user_plocation:
                count+=1
                value += k+';'+ v + '\t'
        call_len = len(self.call_record_map.keys())
        radio = count*1.0/(call_len or 1)
        r = minRule()
        r.name = '通话记录中电话号码与申请人同一手机归属地的比例'
        r.value = value
        if radio>0 and radio<=0.3:
            r.score = 30
        elif radio>0.3 and radio<=0.5:
            r.score = 100
        elif radio>0.5 and radio<=1:
            r.score = 70
        elif radio>1:
            r.score = 20
        r.source = '{"count":%s,"calllen":%s}'%(str(count),str(call_len))
        r.feature_val = "%.2f"%(radio)
        return r

    '''短信记录中电话号码与申请人同一手机归属地的比例'''
    def smssame_location_with_userphone(self,basedata):
        user_plocation = basedata.user_plocation
        count=0
        value=''
        for k,v in self.sms_record_map.items():
            location=v.split('-')
            if location[1] in user_plocation or location[0] in user_plocation:
                count+=1
                print k,v,user_plocation
                value+=k+';'+v+'\t'

        sms_len = len(self.sms_record_map.keys())
        radio = count*1.0/(sms_len or 1)
        r = minRule()
        r.name = '短信记录中电话号码与申请人同一手机归属地的比例'
        r.value = value
        if radio>0 and radio<=0.3:
            r.score = 30
        elif radio>0.3 and radio<=0.5:
            r.score = 100
        elif radio>0.5 and radio<=1:
            r.score = 70
        elif radio>1:
            r.score = 20
        r.source = '{"count":%s,"calllen":%s}'%(str(count),str(sms_len))
        r.feature_val = "%.2f"%(radio)
        return r

    '''是否设置21呼叫转移'''
    def set_21(self,basedata):
        r=minRule()
        r.name='是否设置21呼叫转移'
        r.score=0
        value = []
        for c in basedata.contacts:
            if c.phone[0:2] =='21' or c.phone[0:3] =='*21' or c.phone[0:3]=='#21':
                value.append(
                    c.name+';'+c.phone+';'+c.phone_location
                )
        if value:
            r.score = 10
            r.value = '\t'.join(value)
            r.feature_val = str(len(value))+'个号码被设置'
            return r
        r.value = '无'
        r.feature_val = str('没有号码被设置')
        r.score=100
        return r 

    '''是否电话被催收'''
    def is_dunning_call(self):
        r=minRule()
        r.name=u'是否被催收'
        r.score=0
        value = []
        for k,v in self.call_record_map.items():
            if k in self.dunning_map:
                value.append(k)
        if value:
            r.score=10
            r.value='\t'.join(value)
            r.feature_val = '被电话催收过%s次'%(str(len(value)))
            return r
        r.name = '没有被电话催收过'
        r.feature_val = '无'
        r.score=100
        return r

    '''是否被短信催收'''
    def is_dunning_sms(self):
        r=minRule()
        r.name=u'是否短信被催收'
        r.score=0
        value=[]
        for k,v in self.sms_record_map.items():
            if k in self.dunning_map:
                value.append(k)
        if value:
            r.score=10
            r.value=value
            r.feature_val = '被短信催收过%s次'%(str(len(value)))
            return r
        
        r.score=100
        r.value='短信不含催收号码'
        r.feature_val = '无'
        return r

    '''手机归属地与上网所在地一致'''
    def phone_location_int_net_location(self,basedata):
        net_map={}
        user_plocation=basedata.user_plocation
        r=minRule()
        r.name = '手机归属地与上网所在地一致'
        user_plocation=basedata.user_plocation
        for net in basedata.sp_net:
            if net.net_location not in net_map:
                net_map[net.net_location]=0
            net_map[net.net_location] += 1
        r.value = '\t'.join([k+';出现次数:'+ str(v) +'次' for k,v in net_map.items()])
        if user_plocation not in net_map:
            r.score=0
            r.feature_val = '不一致'
            r.source = str(0) #0：不一致
            return r
        r.source = 1
        r.score=100
        return r

    '''与021,0755通话次数'''
    def call_with_021_0755(self,basedata):
        resmap={}
        for call in basedata.sp_calls:
            try:
                kk=None
                phone=call.phone
                datastr='通话开始时间:'+str(call.calling_time)+';通话时长:'+str(call.calling_duration)+'s;'
                datastr+='号码:'+phone+';'+';信息来源:'+call.source
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

        r = minRule()
        r.name = '与021,0755通话次数'
        if resmap:
            r.value='\t'.join([ k+''+'\t'.join(v)  for k,v in resmap.items()])
            r.feature_val = '出现%s次'%(len(resmap.keys))   
            r.score=10
            return r
        r.score=100
        r.feature_val = '未出现'
        r.value = '0'
        return r

    '''申请号与本机有通话'''
    def userphone_in_calls_or_sms(self,basedata):
        user_phone=basedata.user_phone
        r = minRule()
        r.score=0
        r.value=''
        r.name = '申请号与本机有通话'
        r.feature_val = '无'
        if user_phone in self.sms_record_map or user_phone in self.sms_record_map:
            r.score=100
            r.value+=user_phone+'\t'
            r.feature_val = '有'
        return r
    '''通话记录长度'''
    def call_record_len(self):
        call_len = len(self.call_record_map.keys())
        r = minRule()
        r.name = '通话记录长度'
        r.feature_val = str(call_len)
        if call_len<30:
            r.score=10
        elif call_len>=30 and call_len<50:
            r.score=20
        elif call_len>=50 and call_len<100:
            r.score=40
        elif call_len>=100:
            r.score = 100
        r.value='暂不显示通话记录'
        return r

    '''短信记录长度'''
    def sms_record_len(self):
        sms_len = len(self.sms_record_map.keys())
        r = minRule()
        r.name = '短信记录长度'
        r.feature_val = str(sms_len)
        if sms_len<30:
            r.score=10
        elif sms_len>=30 and sms_len<50:
            r.score=20
        elif sms_len>=50 and sms_len<100:
            r.score=40
        elif sms_len>=100:
            r.score = 100
        r.value='暂不显示短信记录'
        return r


    def get_score(self):
        min_rmap = self.min_rule_map
        
        call_record_len_s=min_rmap[20001].score*0.1  #通话记录长度是否合理
        sms_record_len_s = min_rmap[20002].score*0.1 #短信记录长度是否合理            
        incharge_amount = min_rmap[20003].score*0.1 #半年内充值金额
        incharge_times = min_rmap[20004].score*0.05 #半年内充值次数
        incharge_inter_days = min_rmap[20005].score*0.05 #半年内平均充值间隔(天/次)
        call_in_times_s = min_rmap[20006].score*0.025 #半年内主叫次数
        call_in_duration = min_rmap[20007].score*0.025  #半年内主叫时长
        call_out_times = min_rmap[20008].score*0.025 #半年内被叫次数
        call_out_duration = min_rmap[20009].score*0.025 #半年内被叫时长
        call_in_contact = min_rmap[20010].score*0.05 #通话记录电话号码出现在通讯录的比例
        smssame_in_contact = min_rmap[20011].score*0.05 #短信记录电话号码出现在通讯录中的比例
        callsame_with_idcard = min_rmap[20012].score*0.25 #通话记录电话号码在老家的比例
        smssame_with_idcard = min_rmap[20013].score*0.25 #短信记录电话号码在老家的比例
        callsame_with_userphone = min_rmap[20014].score*0.25 #通话记录中电话号码与申请人同一手机归属地的比例
        smssame_with_userphone = min_rmap[20015].score*0.25 #短信记录中电话号码与申请人同一手机归属地的比例
        set_21 = min_rmap[20016].score*0.1 #是否设置21呼叫转移
        dunning_call = min_rmap[20017].score*0.05  #是否电话被催收
        dunning_sms = min_rmap[20018].score*0.05  #是否被短信催收
        phone_in_netlocation = min_rmap[20019].score*0.05 #手机所在地在上网地点出现次数
        call_with_021_0755 = min_rmap[20020].score*0.05  #与021,0755通话次数
        userphone_in_calls_or_sms = min_rmap[20021].score*0.1 #申请号与本机有通话

        score = call_record_len_s+sms_record_len_s+incharge_amount+incharge_times+incharge_inter_days
        score+=call_in_times_s+call_in_duration+call_out_times+call_out_duration+call_in_contact
        score+=smssame_in_contact+callsame_with_idcard+smssame_with_idcard+callsame_with_userphone
        score+=smssame_with_userphone+set_21+dunning_call+dunning_sms+phone_in_netlocation
        score+=call_with_021_0755+userphone_in_calls_or_sms
        return score

















