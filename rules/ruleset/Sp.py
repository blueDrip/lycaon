#!/usr/bin/env python
# encoding: utf-8
import sys
import os
reload(sys)
import json
import re
from datetime import datetime
sys.setdefaultencoding('utf8')
from rules.raw_data import minRule
from rules.baserule import BaseRule
from rules.base import get_right_datetime
class Sp(BaseRule):
    def __init__(self,basedata):

        self.recharge_map = self.init_recharge_map(basedata)
        self.phone_map=self.init_phonedetail_mp(basedata)

        self.min_rule_map={
            30001:self.incharge_money_in_month(),
            30002:self.call_times_out_his(),
            30003:self.call_times_in_his(),
            30004:self.incharge_interdays(),
            30005:self.name_in_contact(),
        }

    def init_recharge_map(self,basedata):
        mp=json.loads(basedata.sp.recharge)['data']
        charge_mp={}
        for it in mp:
            td=it['payDate']
            key=datetime(int(td[0:4]),int(td[4:6]),int(td[6:8]),int(td[8:10]),int(td[10:12]),int(td[12:14]))
            charge_mp.update({
                key:it['payFee']
            })
        return charge_mp

    def init_phonedetail_mp(self,basedata):    
        mp={}

        for k,v in basedata.sp.phonedetail.items():
            d=re.findall(r"\((.+)\).*",v)
            for it in d:
                itmp=json.loads(it)['data']
                for itt in itmp:
                    if k not in mp:
                        mp[k]=[]
                    mp[k].append(itt)
        return mp

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

    def get_score(self):
        min_rule_map = self.min_rule_map
        incharge_money_score=min_rule_map[30001].score*0.2
        call_time_money_score=min_rule_map[30002].score*0.2
        call_time__in_score=min_rule_map[30003].score*0.2
        name_in_contact_score=min_rule_map[30005].score*0.2
        incharge_interdays=min_rule_map[30004].score*0.2
        score=incharge_money_score+call_time_money_score+call_time__in_score+name_in_contact_score+incharge_interdays
        return score
