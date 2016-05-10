#!usr/bin/env python
# encoding: utf-8
import sys
import os
reload(sys)
import re
sys.setdefaultencoding('utf8')
from rules.base import get_right_datetime
from rules.baserule import  BaseRule
from rules.raw_data import minRule
class JD(BaseRule):
    def __init__(self,basedata):
        self.address_map={}
        self.consume_before_3mon_list=[]
        self.consume_after_list=[]
        self.login_his_map={}
        self.load_data(basedata)
        self.min_rule_map={
            10001:self.is_valid_name(basedata),
            10002:self.is_valid_phone(basedata),
            10003:self.get_huiyuanjibie(basedata),
            10004:self.get_three_month_before_consume(),
            10005:self.get_three_month_after_consume(),
            10006:self.get_laster_login_time_inter(),
            10007:self.get_address(basedata)

        }        


    def init_consume_map(self,consume_str):
        cl = consume_str.strip('##\*\*\*##').replace(u'￥','').split('##***##')
        clist=[]
        for c in cl:
            cc = c.split('###$$$')
            clist.append({
                'time':get_right_datetime(cc[0]),
                'orderid':cc[1],
                'money':float(cc[3])   
            })
        return clist

    def init_login_history_list(self,consume_str):
        login_his=consume_str.strip('##\*\*\*##').split('##***##')
        cmap={}
        for his in login_his:
            h=his.split('###$$$')
            hl=len(h)>1 and h[1].split(' ') or []
            key = get_right_datetime(h[0])
            cmap.update({ key:{
                            'province':hl and hl[1] or 'none',
                            'ciyt':len(hl)>2 and hl[2] or 'none'
                        }
            })
        return cmap


    def load_data(self,basedata):
        self.consume_before_3mon_list=self.init_consume_map(basedata.jd.three_month_before_consume)
        self.consume_after_list = self.init_consume_map(basedata.jd.three_month_consume)
        self.login_his_map= self.init_login_history_list(basedata.jd.loginhistory)


    '''实名认证'''
    def is_valid_name(self,basedata):
        r=minRule()
        ispass=basedata.jd.isrealname
        r.value=-1
        r.score=0
        r.source=ispass

        r.name=u'实名认证'
        if u'验证通过' in ispass:
            r.value=u'验证通过'
            r.score=100
        elif u'验证失败' in ispass:
            r.value=u'验证失败'
            r.score=70
        elif u'未验证' in ispass:
            r.value=u'未验证'
            r.score=20
        else:
            r.value=u'结果未知'
        return r

    def is_valid_phone(self,basedata):
        r=minRule()
        ispass=basedata.jd.isvalidphone
        r.value=-1
        r.score=0
        r.name=u'手机验证'        
        r.source=ispass
        if u'验证通过' in ispass:
            r.value=u'验证通过'
            r.score=100
        elif u'验证失败' in ispass:
            r.value =u'验证失败'
            r.score=70
        elif u'未验证' in ispass:
            r.value =u'未验证'
            r.score=20
        else:
            r.value=u'结果未知'
        return r
    def get_huiyuanjibie(self,basedata):
        r=minRule()
        grade=basedata.jd.huiyuanjibie
        r.value=grade
        r.score=0
        r.source=grade

        r.name=u'会员级别'
        if u'钻石会员'==grade:
            r.score=100
        elif u'金牌会员'==grade:
            r.score=80
        elif u'银牌会员'==grade:
            r.score=60
        return  r

    def get_three_month_before_consume(self):
        r=minRule()
        clist=self.consume_before_3mon_list
        money=0
        r.value=u''
        r.score=0
        for v in clist:
            r.value+= u'\n订单号:%s；时间:%s；金额:%s'%(v['orderid'],str(v['time']),str(v['money']))
            money+=v['money']
        avgm=money/(3.0 or 1)
        if avgm<100:
            r.score=10
        elif avgm>=100 and avgm<300:
            r.score=30
        elif avgm>=300 and avgm<500:
            r.score=80
        elif avgm>=500:
            r.score=100
        r.source='{"times":%s,"money":%s}'%(str(len(clist)),str(money))
        r.name=u'三个月平均消费金额(金额／次数):'+str(avgm)
        return r
    def get_three_month_after_consume(self):
        r=minRule()
        r.value=''
        r.score=0
        clist=self.consume_before_3mon_list
        money=0
        for v in clist:
            #print v['time'],v['orderid'],v['money']
            r.value+= u'\n订单号:%s；时间:%s；金额:%s'%(v['orderid'],str(v['time']),str(v['money']))
            money+=v['money']

        avgm=money/(len(clist) or 1)
        if avgm<100:
            r.score=10
        elif avgm>=100 and avgm<300:
            r.score=30
        elif avgm>=300 and avgm<500:
            r.score=80
        elif avgm>=500:
            r.score=100
        r.source='{"times":%s,"money":%s}'%(str(len(clist)),str(money))
        r.name=u'历史平均消费金额(金额／次数)'+str(avgm)
        return r
    def get_laster_login_time_inter(self):
        r=minRule()
        inter=0
        login_his=self.login_his_map.keys()
        login_his.sort()
        '''排序'''
        r.value=u'\n登陆时间:\n'
        for i in range(0,len(login_his)-1):
            v=login_his[i]
            v_next=login_his[i+1]
            r.value+=str(v)+'\n'
            inter+=(v_next-v).days
        r.value+=str(v_next)+'\n'
        avg_days=inter*1.0/(len(login_his)+1)
        r.name=u'平均登陆时间登陆间隔:'+str(avg_days)
        r.score=100
        return r

    def get_address(self,basedata):
        r=minRule()
        sub_str = re.sub('\t|\n|\r|\s+','',basedata.jd.address)
        sub_list = sub_str.strip('#***#').split('#***#')
        infomp={}
        for adr in sub_list:
            info = adr.replace('###','').split('$$$')
            key=len(info)>2 and  info[1] or None
            value=len(info)>3 and info[3] or None
            if key and key not in infomp:
                infomp[key]=[]
            infomp[key].append(value)
        ss=''
        count_mp={}
        for k,v in infomp.items():
            ss+='收件人:'+k+'\n'
            for it in v:
                ss+='\t地址:'+it+'\n'
                if it not in count_mp:
                    count_mp[it]=0
        r.value=ss
        r.score=0
        count_address=len(count_mp.keys())
        r.name=u'收货地区个数:'+str(infomp and len(count_mp.keys()))
        if count_address<=15:
            r.score=100
        elif count_address>15 and count_address<=30:
            r.score=70
        r.source=str(infomp and len(count_mp.keys()))
        return r
    def get_score(self):
        min_rule_map = self.min_rule_map
        is_valid_name_score=min_rule_map[10001].score*0.2
        is_vphone_score=min_rule_map[10002].score*0.2
        grade_score=min_rule_map[10003].score*0.2
        month_3_score=min_rule_map[10004].score*0.2
        month__score=min_rule_map[10005].score*0.1
        address_score=min_rule_map[10006].score*0.1
        score=is_valid_name_score+is_vphone_score+grade_score+month_3_score+month__score+address_score
        return score
