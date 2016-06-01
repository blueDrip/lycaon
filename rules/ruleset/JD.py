#!usr/bin/env python
# encoding: utf-8
import sys
import os
import re
from rules.base import get_right_datetime
from rules.models import  BaseRule
from rules.raw_data import minRule
from datetime import datetime,timedelta
class JD(BaseRule):
    def __init__(self,basedata):
        self.address_map={}
        self.consume_before_3mon_list=[]
        self.consume_after_list=[]
        self.login_his_map={}
        self.address_info_map={}
        self.load_data(basedata)
        self.min_rule_map={

            30001:self.is_valid_name(basedata),#京东身份证验证
            30002:self.is_valid_phone(basedata),#京东手机验证
            30003:self.get_huiyuanjibie(basedata),#京东会员等级
            30004:self.get_avg_login_integer_days(basedata),#京东半年内平均登陆时间间隔(登陆时间/次数)
            30005:self.get_consume_amount_harf_year(),#京东半年内消费金额
            30006:self.get_consume_times_harf_year(),#半年内消费次数
            30007:self.owner_name_in_address(basedata),#收件人中有申请人
            30008:self.get_address(),#收货地址个数
            30009:self.address_phone_in_contact(basedata),#收件人电话号码出现在通讯录中
            30010:self.address_phone_in_sms(basedata),#收件人出现下短信中
            30011:self.address_phone_in_call(basedata),#收件人出现在通话记录中
            30012:self.owner_phone_location_in_address(basedata),#收货地址中包含申请人所在地
            30013:self.valid_email(basedata),#邮箱验证
            30014:self.is_open_ious(basedata),#是否开通白条
            30015:self.ious_amount(basedata),#白条额度
            30016:self.can_use_ious_amount(basedata),#可用京东白条额度
            30017:self.consume_ious_amount(basedata),#已用京东白条额度
            30018:self.repay_ious_amount_one_week(basedata),#一周内待还金额
            30019:self.phone_bankinfo(basedata),#绑定银行卡中有申请人手机号
            #30012:None,#半年内是否出现消费断档

        }        
    def init_consume_map(self,consume_str,basedata):
        cl_str = consume_str.strip('##\*\*\*##').replace(u'￥','')
        cl = []
        if '##***##' in cl_str:
            cl = cl_str.split('##***##')
        clist=[]
        now=basedata.create_time
        for c in cl:
            cc = c.split('###$$$')
            kk=get_right_datetime(cc[0])
            if not kk:
                continue
            if kk>now-timedelta(180) and kk<=now:
                clist.append({
                    'time':kk,
                    'orderid':cc[1],
                    'money':float(cc[3])   
                })
        return clist
    def init_login_history_list(self,consume_str):
        login_his_str=consume_str.strip('##\*\*\*##')
        login_his = []
        if '##***##' in login_his_str:
            login_his = login_his_str.split('##***##')
        cmap={}
        for his in login_his:
            h=his.split('###$$$')
            hl=len(h)>1 and h[1].split(' ') or []
            key = get_right_datetime(h[0])
            if not key:
                continue
            cmap.update({ key:{
                            'country':hl and hl[0] or 'none',
                            'province':len(hl)>1 and hl[1] or 'none',
                            'city':len(hl)>2 and hl[2] or 'none'
                        }
            })
        return cmap
    def init_info_mp(self,basedata):
        sub_str = re.sub('\t|\n|\r|\s+','',basedata.jd and basedata.jd.address or '')
        sub_list_str = sub_str.strip('#***#')
        sub_list = []

        if '#***#' in sub_list_str:
            sub_list = sub_list_str.split('#***#')

        infomp={}
        for adr in sub_list:
            info = adr.replace('###','').split('$$$')
            key=len(info)>2 and  info[1] or None
            value=len(info)>3 and info[3] or None
            phone=len(info)>7 and info[7] or None
            tel_phone=len(info)>9 and info[9] or None
            email=len(info)>11 and info[11] or None
            if not key:
                continue
            if key and key not in infomp:
                infomp[key]=[]
            infomp[key].append({
                'value':value,
                'phone' :str(phone),
                'tel_phone':tel_phone,
                'email':email
            })

        return infomp

    def load_data(self,basedata):
        three_month_before_consume = basedata.jd and basedata.jd.three_month_before_consume or ''
        self.consume_before_3mon_list=self.init_consume_map(three_month_before_consume,basedata)

        three_month_consume = basedata.jd and basedata.jd.three_month_consume or ''
        self.consume_after_list = self.init_consume_map(three_month_consume,basedata)

        loginhistory = basedata.jd and basedata.jd.login_history or ''
        self.login_his_map= self.init_login_history_list(loginhistory)

        self.address_info_map = self.init_info_mp(basedata)

    '''身份证认证'''
    def is_valid_name(self,basedata):
        r=minRule()
        ispass=basedata.jd and basedata.jd.indentify_verified or u'unknown'
        r.score=0
        r.source=ispass
        r.name=u'身份证认证'
        if u'unknow' in ispass:
            r.value = u'unknow'
        elif u'验证通过' in ispass:
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
        r.feature_val = r.value
        return r
    '''手机验证'''
    def is_valid_phone(self,basedata):
        r=minRule()
        ispass=basedata.jd and basedata.jd.phone_verifyied or u'unknown'
        r.score=0
        r.name=u'手机验证'        
        r.source=ispass
        if u'unknow' in ispass:
            r.value = u'unknow'
        elif u'验证通过' in ispass:
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
        r.feature_val = r.value
        return r
    '''会员级别'''
    def get_huiyuanjibie(self,basedata):
        r=minRule()
        grade=basedata.jd and basedata.jd.user_level or u'unknow'
        r.value=grade
        r.score=0
        r.source=grade
        r.name=u'会员级别'
        if u'unknow' in grade:
            r.score = 0
        elif u'钻石会员'==grade:
            r.score=100
        elif u'金牌会员'==grade:
            r.score=80
        elif u'银牌会员'==grade:
            r.score=60
        r.feature_val = grade
        return  r
    #京东平均登陆时间间隔(登陆时间/次数)
    def get_avg_login_integer_days(self,basedata):
        r=minRule()
        inter=0
        login_his=self.login_his_map.keys()
        login_his.sort()
        '''排序'''
        for i in range(0,len(login_his)-1):
            v=login_his[i]
            v_next=login_his[i+1]
            inter+=(v_next-v).days

        r.value = u'登陆时间:'+ '\t' +'\t'.join([ str(it) for it in login_his ])
        avg_days=inter*1.0/(len(login_his) or 1)
        r.name=u'平均登陆时间登陆间隔'
        r.feature_val = str(int(avg_days))+u'天/次'
        r.source = str(inter)
        r.score=100
        if avg_days>0 and avg_days<=5:
            r.score=100
        elif avg_days>5 and avg_days<=15:
            r.score=80
        elif avg_days>15 and avg_days<=30:
            r.score=60
        elif avg_days>30:
            r.score=40
        return r

    #半年内消费金额
    def get_consume_amount_harf_year(self):
        consume_list=self.consume_after_list
        consume_list.extend(self.consume_before_3mon_list)
        amount=0
        value = []
        for it in consume_list:
            amount+=it['money']
            value.append(
                'order:'+it['orderid']+'; money:'+str(it['money'])+'; time:'+str(it['time'])
            )
        r=minRule()
        r.score=0
        r.value='\t'.join(value)
        r.source=str(amount)
        r.name=u'半年内消费金额'
        r.feature_val = str(amount)+u'元'
        if amount>0 and amount<=500:
            r.score=20
        elif amount>500 and amount<=1000:
            r.score=50
        elif amount>1000 and amount<=2000:
            r.score=70
        elif amount>2000 and amount<=3000:
            r.score=80
        elif amount>3000:
            r.score=100
        return r
    #半年内消费次数
    def get_consume_times_harf_year(self):
        consume_list=self.consume_after_list
        consume_list.extend(self.consume_before_3mon_list)
        times = len(consume_list)
        r = minRule()
        r.score = 0
        r.name = u'半年内消费次数'
        value=[ 'order:'+it['orderid']+ '; time:'+str(it['time']) +u'; 1次' for it in consume_list]
        r.value = '\t'.join(value)
        r.source=str(times)
        r.feature_val = str(times)
        if times>0 and times<=10:
            r.score=50
        elif times>10 and times<=30:
            r.score=80
        elif times>30:
            r.score=100
        return r
    #不同的收货地址个数
    def get_address(self):
        r=minRule()
        ss=''
        count_mp={}
        for k,v in self.address_info_map.items():
            ss+=u'收件人:'+k+'\t'
            for it in v:
                ss+=u'地址:'+it['value']+'\t'
                if it['value'] not in count_mp:
                    count_mp[it['value']]=0
        r.value=ss
        r.score=0
        count_address = len(count_mp.keys())
        r.name=u'不同的收货地址个数'
        if count_address<=15:
            r.score=100
        elif count_address>15 and count_address<=30:
            r.score=70
        r.source=str( len(count_mp.keys()))
        r.feature_val = str(count_address)+u'个'
        return r

    #收件人电话号码出现在通讯录中
    def address_phone_in_contact(self,basedata):
        phone_list=[]
        value=[]
        for k,v in self.address_info_map.items():
            for it in v:
                if it['phone'] not in phone_list:
                    phone_list.append(it['phone'])
        for c in basedata.contacts:
            if len(c.phone)>=11:
                
                str_=c.phone[0:3]+'****'+c.phone[7:]
                if str_ in phone_list:
                    value.append(str_)
        r = minRule()
        r.name=u'收件人出现在通讯录中'
        r.score = 0
        r.source = str(len(value))
        r.feature_val = u'无'
        if value:
            r.value = '\t'.join(value)
            r.score=100
            r.feature_val = u'出现个数:%s'%(str(len(value)))
        return r
    #收件人号码出现下短信中
    def address_phone_in_sms(self,basedata):
        phone_list=[]
        value=[]
        for k,v in self.address_info_map.items():
            for it in v:
                if it['phone'] not in phone_list:
                    phone_list.append(it['phone'])        
        for sms in basedata.sp_sms:
            if len(sms.phone)>=11:
                str_=sms.phone[0:3]+'****'+sms.phone[7:]
                if str_ in phone_list:
                    value.append(str_)
        r = minRule()
        r.name=u'与收件人有短信联系'
        r.score = 0
        r.source = str(len(value))
        r.feature_val = u'无'
        if value:
            r.value = '\t'.join(value)
            r.score=100
            r.feature_val = u'出现个数:%s'%(str(len(value)))
        return r
    #收件人号码出现在通话记录中
    def address_phone_in_call(self,basedata):
        phone_list=[]
        value=[]
        for k,v in self.address_info_map.items():
            for it in v:
                if it['phone'] not in phone_list:
                    phone_list.append(it['phone'])
        for c in basedata.sp_calls:
            if len(c.phone)>=11:
                str_=c.phone[0:3]+'****'+c.phone[7:]
                if str_ in phone_list:
                    value.append(str_)
        r = minRule()
        r.name= u'与收件人有电话联系'
        r.score=0
        r.source = str(len(value))
        r.feature_val = u'无'
        if value:
            r.score=100
            r.value='\t'.join(value) 
            r.feature_val = u'有%s联系'%(str(len(value)))
        return r

    #手机归属地中出现在收货地址中
    def owner_phone_location_in_address(self,basedata):
        value=[]
        user_phone_location=basedata.user_plocation
        for k,v in self.address_info_map.items():
            for it in v:
                if it['value'] in user_phone_location:
                    value.append(
                        k+';'+it['phone']+';'+it['value']
                    )
        r = minRule()
        r.name=u'申请用户手机归属地出现在收货地址中'
        r.value = '\t'.join(value)
        r.score = 0
        r.feature_val = u'无'
        r.source = str(len(value))
        if value:
            r.score=100
            r.feature_val = u'出现%s个'%(str(len(value)))
        return r

    #收件人中有申请人
    def owner_name_in_address(self,basedata):
        owner_name=basedata.username
        value=[]
        for k,v in self.address_info_map.items():
            if k == owner_name:
                value.append(
                    k+';'+'\t'.join([ it['phone']+';'+it['value'] for it in v])
                )
        r = minRule()
        r.name=u'收件人中有申请人'
        r.value= '\t'.join(value)
        r.score=0
        r.feature_val = str(len(value))+'个'
        r.source = str(len(value))
        if value:
            r.score=100
        return r
    #半年内出现消费断档的天数
    def grp_consume_in_harf_year(self,basedata):
        pass

    #邮箱认证
    def valid_email(self,basedata):
        ispass=basedata.jd and basedata.jd.email_verified or u'unknown'
        r = minRule()
        r.name=u'是否邮箱验证'
        r.source=ispass
        if u'unknown' in ispass:
            r.value = u'unknown'
        elif u'验证通过' in ispass:
            r.value=u'验证通过'
            r.score=100
        elif u'验证失败' in ispass:
            r.value=u'验证失败'
            r.score=70
        else:
            r.value=u'未验证'
            r.score=20
        r.feature_val = r.value
        return r

    #是否开通白条
    def is_open_ious(self,basedata):
        isopen=basedata.jd and basedata.jd.baitiao or {}
        flag=False
        r = minRule()
        r.name = u'是否开通白条'
        r.score = 30
        if isopen:
            flag = u'isOpen' in isopen and isopen[u'isOpen'] or False
        if flag:
            r.value = u'unknown'
        else:
            r.value = u'开通'
            r.score = 100
        r.source = flag
        r.feature_val = r.value
        return r

    #白条额度
    def ious_amount(self,basedata):
        bt=basedata.jd and basedata.jd.baitiao or {}
        r = minRule()
        r.name = u'白条额度'
        r.score = 10
        if bt:
            flag = u'totalAmount' in bt and float(bt[u'totalAmount'].replace(',','')) or 'unknown'
        r.value = str(flag)
        if flag>=0 and flag<1000:
            r.score = 30
        elif flag>=1000 and flag<2000:
            r.score = 50
        elif flag>=2000 and flag<3000:
            r.score = 60
        elif flag>=4000 and flag<5000:
            r.score = 80
        else:
            r.score = 100
        r.source = str(flag)
        r.feature_val = str(flag)
        return r                

    #可用京东白条额度
    def can_use_ious_amount(self,basedata):

        bt=basedata.jd and basedata.jd.baitiao or {}
        r = minRule()
        r.name = u'可用白条额度'
        r.score = 10
        if bt:
            flag = u'avaliableAmount' in bt and float(bt[u'avaliableAmount'].replace(',','')) or 'unknown'
        r.value = str(flag)
        if flag>=0 and flag<1000:
            r.score = 30
        elif flag>=1000 and flag<2000:
            r.score = 50
        elif flag>=2000 and flag<3000:
            r.score = 60
        elif flag>=4000 and flag<5000:
            r.score = 80
        else:
            r.score = 100
        r.source = str(flag)
        r.feature_val = str(flag)
        return r

    #已用京东白条额度
    def consume_ious_amount(self,basedata):

        bt=basedata.jd and basedata.jd.baitiao or {}
        r = minRule()
        r.name = u'已用白条额度'
        r.score = 10
        if bt:
            flag = u'consumeAmount' in bt and float(bt[u'consumeAmount'].replace(',','')) or 'unknown'
        r.value = str(flag)
        if flag>=0 and flag<1000:
            r.score = 30
        elif flag>=1000 and flag<2000:
            r.score = 50
        elif flag>=2000 and flag<3000:
            r.score = 60
        elif flag>=4000 and flag<5000:
            r.score = 80
        else:
            r.score = 100
        r.source = str(flag)
        r.feature_val = str(flag)
        return r

    #一周内待还金额
    def repay_ious_amount_one_week(self,basedata):

        bt=basedata.jd and basedata.jd.baitiao or {}
        r = minRule()
        r.name = u'一周内待还白条额度'
        r.score = 10
        if bt:
            flag = u'pending' in bt and float(bt[u'pending'].replace(',','')) or 'unknown'
        r.value = str(flag)
        if flag>=0 and flag<1000:
            r.score = 30
        elif flag>=1000 and flag<2000:
            r.score = 50
        elif flag>=2000 and flag<3000:
            r.score = 60
        elif flag>=4000 and flag<5000:
            r.score = 80
        else:
            r.score = 100
        r.source = str(flag)
        r.feature_val = str(flag)
        return r

    #绑定银行卡中有申请人手机号
    def phone_bankinfo(self,basedata):
        bankinfo=basedata.jd and basedata.jd.bankinfo or u'unknown'
        up=basedata.user_phone
        bank_phone =  up[:3]+'****'+up[7:]
        r=minRule()
        r.name=u'绑定银行卡中有申请人手机号'
        r.score = 20
        r.value = bankinfo
        if u'unknown' in bankinfo:
            r.score = 10
            r.feature_val = u'unknown'
        elif bank_phone in bankinfo:
            r.score = 100
            r.feature_val = u'有'
        r.source = r.feature_val
        return r

    def get_score(self):
        min_rmap = self.min_rule_map
        valid_name = min_rmap[30001].score*0.1 #京东实名验证
        valid_phone = min_rmap[30002].score*0.06  #京东手机验证
        grade = min_rmap[30003].score*0.05 #京东会员等级
        avg_login_days = min_rmap[30004].score*0.05 #京东半年内平均登陆时间间隔(登陆时间/次数)
        consume_amount = min_rmap[30005].score*0.05 #京东半年内消费金额
        consume_times = min_rmap[30006].score*0.05 #半年内消费次数
        owner_name_in_address = min_rmap[30007].score*0.1 #收件人中有申请人
        address = min_rmap[30008].score*0.03 #收货地址个数
        address_phone_in_contact = min_rmap[30009].score*0.1 #收件人电话号码出现在通讯录中
        address_phone_in_sms = min_rmap[30010].score*0.1 #收件人出现下短信中
        address_phone_in_call = min_rmap[30011].score*0.1 #收件人出现在通话记录中
        owner_phone_location_in_address = min_rmap[30012].score*0.07 #申请人手机归属地出现在收货地址中

        valid_email = min_rmap[30013].score*0.02 #邮箱验证
        open_ious = min_rmap[30014].score*0.02 #是否开通白条
        ious_amount = min_rmap[30015].score*0.02 #白条额度
        can_use_ious_amount = min_rmap[30016].score*0.02 #可用京东白条额度
        consume_ious_amount = min_rmap[30017].score*0.02 #已用京东白条额度
        repay_ious_one_week = min_rmap[30018].score*0.02 #一周内待还金额
        phone_bankinfo = min_rmap[30019].score*0.02 #绑定银行卡中有申请人手机号


        score=valid_name+valid_phone+grade+avg_login_days
        score+=consume_amount+consume_times+owner_name_in_address
        score+=address+address_phone_in_contact+address_phone_in_sms
        score+=address_phone_in_call+owner_phone_location_in_address

        score+=valid_email+open_ious+ious_amount
        score+=can_use_ious_amount+consume_ious_amount
        score+=repay_ious_one_week+phone_bankinfo

        return score  

