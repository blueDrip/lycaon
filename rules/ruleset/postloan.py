#!/usr/bin/env python
# encoding: utf-8

import sys
import os
from django.conf import settings
import traceback
import socket
import time
import urllib
import json
import datetime
import math

import logging
import StringIO
import re
from rules.util.langconv import Converter
from rules.ext_api import EXT_API
from rules.raw_data import minRule
from rules.models import BaseRule
#logger = logging.getLogger('django.rules')
#logger.setLevel(logging.INFO)

def pre_contacts(oinfo,parent_l,parent_l_ch,spouse_l):
    parent_list=parent_l
    parent_list_ch=parent_l_ch
    spouse_list=spouse_l 
    #city_list=oinfo.exp.phone_map.values()
    tmp_contacts_l=oinfo.contacts
    #for u in oinfo.good_contacts:
    #    tmp_contacts_l.extend(u)


    for c in tmp_contacts_l:
        try:
            if not c.name:
                continue
            #去掉空格
            c.name=re.sub('\s+(?!$)','',c.name) or c.name
            #繁体转简
            c.name = Converter('zh-hans').convert(c.name)
            #小写转大写
            c.name=c.name.upper()
            #去掉无效词
            invalid_word_list=[u'联通号',u'移动号',u'电信号',u'手机',u'新号',u'联通',u'移动',u'电信',u'小号',u'大号',u'新',u'号']
            for item in invalid_word_list:
                c.name=item in c.name and c.name.replace(item,'') or c.name
            #print '去掉无效词>>>>>>>>>>>>>>>>',c.name
            #for item in city_list:
            #    e=c.name.index(item)-1
            #    c.name=item in c.name and c.name[:e]
            #去掉括号
            m=re.match(ur'.*[(（](.*)[)）]',c.name)
            parent_list.extend(parent_list_ch)
            if m:
                flag=is_m_f_in_law(m.group(1),spouse_list) or m.group(1) in parent_list
                c.name=flag and m.group(1) or c.name.replace(m.group(1),'')[0:-2]
            #叠词合并
            name=c.name
            c.name=not name.replace(c.name[0],'') and name[0:2] or c.name
            #错别字转换
            wl={
                u'佰':u'伯',u'孃':u'娘',u'女良':u'娘',u'女古':u'姑',u'父巴':u'爸',u'么':u'幺',
                u'父多':u'爹',u'女马':u'妈',u'女审':u'婶',u'家里':u'家',u'佬嘙':u'老婆'
                }
            wl_err=[u'么么哒']
            for k in wl.keys():
                if k in c.name and not c.name in wl_err:
                    c.name=c.name.replace(k,wl[k])
            #去掉姓名后的单个数字
            c.name=not c.name.isdigit() and re.sub(ur'([0-9]+$)','',c.name) or c.name

            #去掉字母,空格，特殊字符（TA,N)
            if not c.name.encode('utf-8').isalpha():
                c.name=u'TA' != c.name[0:2] and u'N' !=c.name[0] and re.sub(ur'([^\u4E00-\u9FA5\uac00-\ud7ff0-9]|[的]+)','',c.name) or c.name
            #顺序词转为N 
            prex_list=[u'大',u'二',u'三',u'四',u'五',u'六',u'七',u'八',u'九',u'小',u'幺',u'1',u'2',u'3',u'4',u'5',u'6',u'7',u'8',u'9']
            c.name=not c.name[0:2].isdigit() and  c.name[0] in prex_list and c.name.replace(c.name[0],'N',1) or c.name
            #去掉家
            if c.name not  in [u'老家',u'家里',u'家']:
                c.name=c.name[-1:]==u'家' and c.name[0:-1] not in spouse_list and c.name[0:-1] or c.name
                c.name=c.name[0]==u'家' and c.name[1:] not in spouse_list and c.name[1:] or c.name
        except:
            print 'pre err'            
            continue
    return tmp_contacts_l


#A类(10分)
def is_father(name,f_l):
    for it in f_l:
        if it in name:
            return True
    return False
def is_mather(name,m_l):
    for it in m_l:
        if it in name:
            return True
    return False
def is_home(name):
    strlist=[u'家',u'家里',u'FAMILY',u'HOME',u'爸爸妈妈',u'爸妈',u'父母']
    for it in strlist:
        if it in name:
            return True
    return False
    
def is_m_f_blood(name,parent_list,parent_adj_list,parent_list_ch):
    parent_noun_list=parent_list
    parent_adj_list=parent_adj_list
    parent_noun_list_ch=parent_list_ch
    parent_adj_list_ch=[u'MY',u'FAMILY',u'DEAR']
    fl=['老家','家','家里','FAMILY','HOME','爸爸妈妈','爸妈','父母']
    if name.encode('utf-8') in fl:
        return True
    if name in parent_noun_list or name in parent_noun_list_ch:
        return True
    if len(name)>=2:
        for i in range(1,5):
            if name[0:i] in parent_adj_list and name[i:] in parent_noun_list:
                return True
            elif name[0:i] in parent_noun_list and name[i:] in parent_adj_list:
                return True             
        for i in range(1,9):
            if name[0:i] in parent_adj_list_ch and name[i:] in parent_noun_list_ch:
                return True
            if name[0:i] in parent_noun_list_ch and name[i:] in parent_adj_list_ch:
                return True
    return False

#B1类(8分)
def is_m_f_in_law(name,spouse_list):

    spouse_noun_list=spouse_list
    fl=['继父','后爸','继母','后妈','公公','他爸','他爸爸','婆婆','他妈','他妈妈',          
        '岳父','岳丈','老丈人','她爸','她爸爸','TA爸','岳母','丈母娘','她妈','她妈妈','TA妈']
    if name.encode('utf-8') in fl:
        return True
    suffix_list=[u'爸',u'妈',u'爸爸',u'妈妈',u'他爸',u'他妈',
                 u'她爸',u'她妈',u'他爸爸',u'他妈妈',u'她爸爸',u'她妈妈',u'家']
    for i in range(1,13):
        #print name[0:i],name[i:]
        if name[0:i] in spouse_noun_list and name[i:] in suffix_list: 
            return True
    return False

#B2类(5分)
def is_grandparent(name):
    grandparent_list=['爷','爷爷','奶奶','祖父','奶','祖母','外公','姥','外婆','老老','姥爷','姥姥']
    return name.encode('utf-8') in grandparent_list

#B3类(5分)

def is_uncle_aunt_blood(name):
    name=name.encode('utf-8')
    uncle_list=['叔','N叔','老叔','叔叔','伯伯','N伯伯','N伯','N爹','N爷','N爸爹']
    aunt_list=['姑','N姑','老姑','姑姑','N姑姑','姑妈','N姑妈']

    mother_brother_list=['舅','N舅','老舅','舅舅','N舅舅']
    mother_sister_list=['姨','N姨','老姨','姨妈','N姨妈']
    return name in uncle_list or name in aunt_list or name in mother_brother_list or name in mother_sister_list

#B4类(5分)
def is_blood_brother(name):
    name=name.encode('utf-8')
    bl=['哥哥','哥','N哥','老哥','弟弟','弟','N弟','老弟']
    sl=['姐姐','姐','N姐','老姐','家姐','N家姐','妹妹','妹','N妹','老妹']        
    return name in bl or name in sl

#B5类(5分)
def is_male_cousins_sister(name):
    name=name.encode('utf-8')
    bl=['表哥','N表哥','堂哥','N堂哥','N叔子','N伯子','老公哥哥','老公弟弟']
    bl_=['表弟','N表弟','堂弟','N堂弟','N舅子','老婆哥哥','老婆弟弟']

    sl=['表姐','N表姐','堂姐','N堂姐','N姑子','N姑姐','妯娌','老公姐姐','老公妹妹']
    sl_=['表妹','N表妹','堂妹','N堂妹','N姨子','老婆姐姐','老婆妹妹']
    return name in bl or name in bl_ or name in sl or name  in sl_

#B6类(1分)
def is_spouse(name,spouse_list,spouse_adj_list):
    spouse_noun_l=spouse_list
    spouse_adj_l=spouse_adj_list
    if name in spouse_noun_l:
        return True
    for i in range(1,10):
        #print name[0:i],name[i:]
        if name[0:i] in spouse_adj_l and name[i:] in spouse_noun_l:
            return True
        elif name[0:i] in spouse_noun_l and name[i:] in spouse_adj_l:
            return True

    spouse_child_l=[u'孩',u'孩子',u'孩纸',u'孩儿',u'娃',u'娃儿',u'宝',u'宝贝']
    spouse_relationship_l=[u'他妈',u'他爸',u'他妈妈',u'他爸爸',u'他娘',u'他爹',
                           u'她妈',u'她爸',u'她妈妈',u'她爸爸',u'她娘',u'她爹']
    for i in range(1,5):
        #print name[0:i],name[i:]
        if name[0:i] in spouse_child_l and name[i:] in spouse_relationship_l:
            return True
        elif name[0:i] in spouse_relationship_l and name[i:] in spouse_child_l:
            return True

    return False

#C3类(5分)
def is_uncle_aunt_in_law(name):
    name=name.encode('utf-8')
    uncle_list=['婶婶','N婶婶','婶','N婶','N娘','N妈','婶母']    
    uncle_list_=['姑父','N姑父','姑夫','N姑夫','姑爹','N姑爹','姑丈','大古夫']

    aunt_list=['舅妈','N舅妈','舅母','N舅母','舅婆','N舅婆']
    aunt_list_=['姨夫','N姨夫','姨父','N姨父','姨爹','N姨爹']       
    return name in uncle_list or name in uncle_list_ or name in aunt_list or name in aunt_list_
#C4类(5分)
def is_brother_sister_in_law(name):
    r_in_law_list=['嫂子','N嫂子','嫂','N嫂','弟媳','N弟媳','姐夫','N姐夫','妹夫','N妹夫','弟妹','N弟妹']
    return name.encode('utf-8') in r_in_law_list
#兄妹
def is_b_s(name):
    return is_brother_sister_in_law(name) or is_blood_brother(name) or is_male_cousins_sister(name)        
#叔，伯，表，姑，舅
def is_uncle_aunt(name):
    return is_uncle_aunt_in_law(name) or is_uncle_aunt_blood(name)


class PostLoanNewRule(BaseRule):
    
    def __init__(self,basedata):
        #self.ext_api = EXT_API()
        self.m_f_list = []
        self.relative_list =[]
        self.tongshi_list = []
        
        parent_noun_file=settings.P_NOUN_FILE
        parent_adj_file=settings.P_ADJ_FILE
        parent_noun_file_ch=settings.P_NOUN_FILE_CH
        spouse_noun_file=settings.LOVER_NOUN_FILE
        spouse_adj_file=settings.LOVER_ADJ_FILE

        parent_dict_new=settings.P_PARENT_DICT_NEW_CONF                   
    
 
        self.parent_list=self.init_post_loan_list(parent_noun_file)
        self.parent_adj_list=self.init_post_loan_list(parent_adj_file)
        self.parent_list_ch=self.init_post_loan_list(parent_noun_file_ch)
        self.spouse_list=self.init_post_loan_list(spouse_noun_file)
        self.spouse_adj_list=self.init_post_loan_list(spouse_adj_file)
        self.f_m_list=self.init_f_m_list(parent_dict_new)

    #是否为本人
    # 1.通讯录长度合理>30
    # 2.通讯录中亲属父母至少有一个
    def base_line(self,basedata):
        clen = len(basedata.contacts)
        self.chef_map={'通讯录长度个数':clen}
        #if clen<30:
        #    basedata.ucl=None


    def load_rule_data(self,basedata):
        self.load_data(basedata)
        self.min_rule_map={
            50001:self.get_contact_len(basedata),#通讯录长度
            50002:self.parents_len_in_contact(basedata),#父母个数
            50003:self.parents_location_same_with_idCard(basedata),#.父母在老家的个数比例
            50004:self.get_parent_call_duration(basedata),#父母通话时长
            50005:self.get_parent_call_times(basedata),#父母通话次数
            50006:self.relative_len_in_contact(basedata),#亲属个数
            50007:self.relative_location_same_with_idcard(basedata),#亲属在老家的个数比例
            50008:self.get_relative_call_duration(basedata),#亲属的通话时长
            50009:self.get_relative_call_times(basedata),#亲属通话次数
        }

    #基本验证
    def is_basic(self,basedata,r):
        if not basedata.ucl:
            r.feature_val = u'unknown'
            r.source = u'unknown'
            r.value = u'unknown'
            r.score = 10
            return r


    def init_post_loan_list(self,conf_file):
        post_loan_list=[]
        f=open(conf_file,'r')
        post_loan_list=[line.replace('\n','').decode('utf-8') for line in f.readlines()]
        f.close()
        return post_loan_list

    def init_f_m_list(self,conf_file):
        m_list=[]
        f_list=[]
        f=open(conf_file,'r')
        flag=False
        for line in f.readlines():
            line=line.replace('\n','')
            if line and line == "#FATHER":
                flag=True
                continue 
            if not flag and line:
                m_list.append(line.decode('utf-8'))
            elif flag and line:
                f_list.append(line.decode('utf-8'))
        f.close()
        return m_list,f_list

    def load_data(self,bd):

        self.tongshi_map = {}
        smap={'':'通信录','0':'短信','1':'通话'}
        
        self.r_relative_map={}
        self.m_f_in_blood_map={}
        self.r_m_f_in_law_map={}
        self.r_uncle_aunt_map={}
        self.r_grand_parent_map={}
        self.r_b_s_map={}
        self.r_lover_map={}
 
        self.mather_mp={}
        self.father_mp={}
        self.home_mp={}
        smap={'':'通信录','0':'短信','1':'通话'}

        self.post_loan_good_contacts=pre_contacts(bd,self.parent_list,self.parent_list_ch,self.spouse_list) 
        for c in self.post_loan_good_contacts:
            if is_m_f_blood(c.name,self.parent_list,self.parent_adj_list,self.parent_list_ch):
                if c.phone not in self.m_f_in_blood_map:
                    self.m_f_in_blood_map[c.phone]=[c.name+'('+smap[c.source]+')'+":"+c.phone_location ]
                    if is_father(c.name,self.f_m_list[1]):
                        self.father_mp[c.phone]=[c.name+'('+smap[c.source]+')'+":"+c.phone_location ]
                    elif is_mather(c.name,self.f_m_list[0]):
                        self.mather_mp[c.phone]=[c.name+'('+smap[c.source]+')'+":"+c.phone_location ]
                    elif is_home(c.name):
                        self.home_mp[c.phone]=[c.name+'('+smap[c.source]+')'+":"+c.phone_location ]
            elif is_m_f_in_law(c.name,self.spouse_list):
                if c.phone not in self.r_m_f_in_law_map:
                    self.r_m_f_in_law_map[c.phone]=[c.name+'('+smap[c.source]+')'+":"+c.phone_location ]
                    self.r_relative_map[c.phone]=[c.name+'('+smap[c.source]+')'+":"+c.phone_location ]
            elif is_grandparent(c.name):
                if c.phone not in self.r_grand_parent_map:
                    self.r_grand_parent_map[c.phone]=[c.name+'('+smap[c.source]+')'+":"+c.phone_location ]
                    self.r_relative_map[c.phone]=[c.name+'('+smap[c.source]+')'+":"+c.phone_location ]
            elif is_uncle_aunt(c.name):
                if c.phone not in self.r_uncle_aunt_map:
                    self.r_uncle_aunt_map[c.phone]=[c.name+'('+smap[c.source]+')'+":"+c.phone_location ]
                    self.r_relative_map[c.phone]=[c.name+'('+smap[c.source]+')'+":"+c.phone_location ]
            elif is_b_s(c.name):
                if c.phone not in self.r_b_s_map:
                    self.r_b_s_map[c.phone]=[c.name+'('+smap[c.source]+')'+":"+c.phone_location ]
                    self.r_relative_map[c.phone]=[c.name+'('+smap[c.source]+')'+":"+c.phone_location ]
            elif is_spouse(c.name,self.spouse_list,self.spouse_adj_list):
                if c.phone not in self.r_lover_map:
                    self.r_lover_map[c.phone]=[c.name+'('+smap[c.source]+')'+":"+c.phone_location ]
                    self.r_relative_map[c.phone]=[c.name+'('+smap[c.source]+')'+":"+c.phone_location ]


    def get_contact_len(self,basedata):
        c=self.post_loan_good_contacts
        r=minRule()
        r.score=0
        clen=len(c)
        r.value=str(clen)
        if clen>30 and clen<=60:
            r.score=20
        elif clen>60 and clen<=90:
            r.score=40
        elif clen>90 and clen<=120:
            r.score=80
        elif clen>120 and clen<=150:
            r.score=100
        elif clen>150 and clen<200:
            r.score=80
        r.name=u'通讯录长度'
        r.source = str(clen)
        r.feature_val = str(clen)
        self.is_basic(basedata,r)
        return r

    def get_parent_call_duration(self,bd):
        r=minRule()
        r.score=0
        r.value=''
        call_list=bd.sp_calls
        duration=0
        fvalue_mp,mvalue_mp,hvalue_mp={},{},{}
        fd,md,hd=0,0,0
        for c in call_list:
            if c.phone in self.father_mp:
                if c.phone not in fvalue_mp:
                    fvalue_mp[c.phone]=0
                else:
                    fvalue_mp[c.phone]+=c.call_duration
                fd+=c.call_duration
            elif c.phone in self.mather_mp:
                if c.phone not in mvalue_mp:
                    mvalue_mp[c.phone]=0
                else:
                    mvalue_mp[c.phone]+=c.call_duration
                md+=c.call_duration                            
            elif c.phone in self.home_mp:
                if c.phone not in hvalue_mp:
                    hvalue_mp[c.phone]=0
                else:
                    hvalue_mp[c.phone]+=c.call_duration
                hd+=c.call_duration
        fvalue,mvalue,hvalue='','',''
        for k,v in fvalue_mp.items():
            fvalue+=self.father_mp[k][0]+u';通话时间:'+str(v)+'\n'
        for k,v in mvalue_mp.items():
            mvalue+=self.mather_mp[k][0]+u';通话时间:'+str(v)+'\n'
        for k,v in hvalue_mp.items():
            hvalue+=self.home_mp[k][0]+u';通话时间:'+str(v)+'\n'
        if fd:
            r.value='Father:\t'+fvalue
        if md:
            r.value+="Mather:\t"+mvalue
        if hd:
            r.value+="Home:\t"+hvalue
        fscore=self.get_score_by_duration(fd)*0.4;
        mscore=self.get_score_by_duration(md)*0.4;
        hscore=self.get_score_by_duration(hd)*0.4;
        r.score=0.4*fscore+mscore*0.3+hscore*0.3;
        r.name=u'父母通话时间'
        r.source = str(fd+md+hd)
        r.feature_val = str(fd+md+hd)+'s'
        self.is_basic(bd,r)
        return r

    def get_score_by_duration(self,duration):
        if duration<=10:
            return 20
        elif duration>10 and duration<=30:
            return 30
        elif duration>30 and duration <=60:
            return 35
        else:
            return 40

    def get_score_by_times(self,times):
        if times<=10:
            return 20
        elif times>10 and times<=30:
            return 30
        elif times>30 and times<=60:
            return 35
        else:
            return 40

    def get_parent_call_times(self,bd):
        r = minRule()
        r.score=0
        r.value=''
        call_list=bd.sp_calls
        duration=0
        fvalue_mp,mvalue_mp,hvalue_mp={},{},{}
        ft,mt,ht=0,0,0
        for c in call_list:
            if c.phone in self.father_mp:
                if c.phone not in fvalue_mp:
                    fvalue_mp[c.phone]=0
                else:
                    fvalue_mp[c.phone]+=1
                ft+=1
            elif c.phone in self.mather_mp:
                if c.phone not in mvalue_mp:
                    mvalue_mp[c.phone]=0
                else:
                    mvalue_mp[c.phone]+=1
                mt+=1
            elif c.phone in self.home_mp:
                if c.phone not in hvalue_mp:
                    hvalue_mp[c.phone]=0
                else:
                    hvalue_mp[c.phone]+=1
                ht+=1
        fvalue,mvalue,hvalue='','',''
        for k,v in fvalue_mp.items():
            fvalue+=self.father_mp[k][0]+u';通话次数:'+str(v)+'\n'
        for k,v in mvalue_mp.items():
            mvalue+=self.mather_mp[k][0]+u';通话次数:'+str(v)+'\n'
        for k,v in hvalue_mp.items():
            hvalue+=self.home_mp[k][0]+u';通话次数:'+str(v)+'\n'
        if ft:
            r.value='Father:\t'+fvalue
        if mt:
            r.value+="Mather:\t"+mvalue
        if ht:
            r.value+="Home:\t"+hvalue

        fscore=self.get_score_by_times(ft)*0.4;
        mscore=self.get_score_by_times(mt)*0.4;
        hscore=self.get_score_by_times(ht)*0.4;
        r.score=0.4*fscore+mscore*0.3+hscore*0.3;
        r.name=u'父母通话次数'
        r.source = str(ft+mt+ht)
        r.feature_val = str(ft+mt+ht)+u'次'
        self.is_basic(bd,r)
        return r

    def get_days_call_parents(self,bd):
        pass

    def get_relative_call_times(self,bd):
        r = minRule()
        r.score=0
        r.value=''
        call_list=bd.sp_calls
        duration=0
        rt=0
        rvalue_mp={}
        for c in call_list:
            if c.phone in self.r_relative_map:
                if c.phone not in rvalue_mp:
                    rvalue_mp[c.phone]=0
                else:
                    rvalue_mp[c.phone]+=1
                rt+=1
        rvalue=''
        for k,v in rvalue_mp.items():
            rvalue+=self.r_relative_map[k][0]+u';通话次数:'+str(v)+'\t'
        if rt:
            r.value='Relatives:\t'+rvalue
        score=0
        if rt<10:
            score=10
        elif rt>=10 and rt<30:
            score=20
        elif rt>=30 and rt<50:
            score=40
        r.score=0.4*score;
        r.name=u'亲属通话次数'
        r.source = str(rt)
        r.feature_val = str(rt)+u'次'
        self.is_basic(bd,r)
        return r

    def get_relative_call_duration(self,bd):
        r = minRule()
        r.score=10
        r.value=''
        call_list=bd.sp_calls
        duration=0
        rvalue_mp={}
        for c in call_list:
            if c.phone in self.r_relative_map:
                if c.phone not in rvalue_mp:
                    rvalue_mp[c.phone]=0
                else:
                    rvalue_mp[c.phone]+=c.call_duration
                duration+=c.call_duration
        rvalue=''
        for k,v in rvalue_mp.items():
            rvalue+=self.r_relative_map[k][0]+u';通话时间:'+str(v)+'\t'
        if duration:
            r.value='Relatives:\t'+rvalue

        score=0
        if duration<1000:
            score=10
        elif duration>=1000 and duration<3000:
            score=20
        elif duration>=3000 and duration<5000:
            score=40
        elif duration>=5000 and duration<8000:
            score=60
        elif duration>=8000 and duration<10000:
            score=80
        elif duration>=10000:
            score=100
        r.score=0.3*score;
        r.name=u'亲属通话时间'
        r.source = str(duration)
        r.feature_val = str(duration)+'s'
        self.is_basic(bd,r)
        return r
    #父母长度在老家比例
    def parents_location_same_with_idCard(self,bd):
        hl = bd.home_location
        pmap=self.father_mp
        pmap.update(self.father_mp)
        pmap.update(self.mather_mp)
        pmap.update(self.home_mp)
        count=0
        value = ''
        for c in bd.contacts:
            location=c.phone_location.split('-')

            if c.phone in pmap:
                if location[1] in hl or location[0] in hl:
                    count+=1
                    value+=c.phone+';'+c.phone_location+'\t'

        radio=count*1.0/(len(bd.contacts) or 1)
        r = minRule()
        r.name=u'父母在老家的个数'
        r.value = value
        r.source = str(count)
        r.score = 20
        if count>0 and count<=2:
            r.score=60
        elif count>2 and count<=3:
            r.score = 80
        elif count>3:
            r.score = 100
        r.feature_val = str(count)+u'个'
        self.is_basic(bd,r)
        return r

    def relative_location_same_with_idcard(self,bd):
        hl = bd.home_location
        count=0
        value=''
        r=minRule()
        r.name=u'亲属在老家的个数'
        r.score = 10
        for c in bd.contacts:
            location=c.phone_location.split('-')
            if c.phone in self.r_relative_map:   
                if location[1] in hl or location[0] in hl:
                    count+=1
                    value+=c.phone+';'+c.phone_location+'\t'

        r.value=value
        if count>0 and count<=3:
            r.score=60
        elif count>3 and count<=5:
            r.score=80
        elif count>5:
            r.score = 100
        r.source = str(count)
        r.feature_val = str(count)+u'个'
        self.is_basic(bd,r)
        return r
    def parents_len_in_contact(self,bd):
        pmap=self.father_mp
        pmap.update(self.father_mp)
        pmap.update(self.mather_mp)
        pmap.update(self.home_mp)
        plen=len(pmap.keys())
        clen=len(bd.contacts)
        r = minRule()
        r.name =u'父母长度'
        r.value = str(plen)
        r.source = str(plen)
        if plen>0 and plen<=1:
            r.score=40
        elif plen>1 and plen<=3:
            r.score=80
        elif plen>3:
            r.score=100
        r.feature_val = str(plen)+u'个'
        self.is_basic(bd,r)
        return r
    def relative_len_in_contact(self,bd):
        rlen = len(self.r_relative_map.keys())
        clen = len(bd.contacts)
        r = minRule()
        r.name =u'亲属长度'
        r.value = '\t'.join([ k+'-'+ v[0] for k,v in self.r_relative_map.items() ])
        r.source = str(rlen)
        if rlen>0 and rlen<=3:
            r.score=40
        elif rlen>3 and rlen<=6:
            r.score=80
        elif rlen>6:
            r.score=100
        r.feature_val = str(rlen)+u'个'
        self.is_basic(bd,r)
        return r
    def get_score(self):
        min_rmap = self.min_rule_map
        contact_len = min_rmap[50001].score*0.1 #通讯录长度
        parents_len_in_contact = min_rmap[50002].score*0.2 #父母个数
        parents_with_idCard = min_rmap[50003].score*0.1 #父母在老家
        parents_call_duration = min_rmap[50004].score*0.1 #父母通话时长
        parents_call_times = min_rmap[50005].score*0.1 #父母通话次数

        relative_len_in_contact = min_rmap[50006].score*0.1 #亲属个数
        relative_with_idcard = min_rmap[50007].score*0.1 #亲属在老家
        relative_call_duration = min_rmap[50008].score*0.1 #亲属通话时长
        relative_call_times = min_rmap[50009].score*0.1 #亲属通话次数
       
        score = contact_len+parents_len_in_contact+parents_with_idCard
        score += parents_call_duration+parents_call_times
        score += relative_len_in_contact+relative_with_idcard
        score += relative_call_duration+relative_call_times
        return score
 


