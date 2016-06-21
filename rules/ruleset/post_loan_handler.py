#coding=utf8

##from __future__ import division
import sys
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'lycaon.settings'
from django.conf import settings
from rules.models import BaseRule

import time
import json
import datetime
import re
from rules.util.langconv import Converter
import logging
import StringIO
logger = logging.getLogger('django.rules')
logger.setLevel(logging.INFO)
from rules.ext_api import EXT_API
import copy
logger = logging.getLogger('django.rules')
logger.setLevel(logging.INFO)


#预处理通讯录
def pre_contacts(contacts,parent_l,parent_l_ch,spouse_l):
    parent_list=parent_l
    parent_list_ch=parent_l_ch
    spouse_list=spouse_l 
    #city_list=oinfo.exp.phone_map.values()
    tmp_contacts_l=[]
    for u in contacts:
        #tmp_contacts_l.extend(u)
        tmp_contacts_l.append(copy.copy(u))
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
            print 'err'            
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
    grandparent_list=['爷','爷爷','奶奶','祖父','奶','祖母','外公','姥','外婆','老老']
    return name.encode('utf-8') in grandparent_list

#B3类(5分)
def is_uncle_aunt_blood(name):
    name=name.encode('utf-8')
    uncle_list=['叔','N叔','老叔','叔叔','伯伯','N伯伯','N伯','N爹','N爷','N爸爹']
    aunt_list=['N姑','老姑','姑姑','N姑姑','姑妈','N姑妈']

    mother_brother_list=['N舅','老舅','舅舅','N舅舅']
    mother_sister_list=['N姨','老姨','姨妈','N姨妈']
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




class PostLoanHandler():

    def __init__(self,ext_api=None):
        self.ext_api = ext_api if ext_api else EXT_API()

        self.relative_map={}
        self.m_f_map={}
        self.lover_map={}

        self.father_map={}
        self.mather_map={}
        self.home_map={}


        #预处理后通讯录
        self.post_loan_good_contacts=[] 
        #加载配置文件
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
        return

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

    def init(self,contacts):

        self.post_loan_good_contacts=pre_contacts(contacts,self.parent_list,self.parent_list_ch,self.spouse_list)
        self.init_map(self.post_loan_good_contacts) 

        return

    def get_parents_list(self,contacts,calls):
        reslist=[]
        call_d_map=self.get_parents_call_duration_list(calls)
        call_n_map=self.get_parents_call_times_list(calls)
        res_map={} 
        for c in contacts:
            if c.phone in self.m_f_map and c.phone not in res_map:
                info={}
                info['phone']=c.phone
                info['name']=self.m_f_map[c.phone]
                info['call_times']=c.phone in call_n_map and call_n_map[c.phone] or 0
                info['call_duration']=c.phone in call_d_map and call_d_map[c.phone] or 0
                info['location']=self.ext_api.get_phone_location(c.phone)
                reslist.append(info)
                res_map[c.phone]=1
        return reslist

    def get_lovers_list(self,contacts,calls):
        reslist=[]
        call_d_map=self.get_relatives_call_duration_list(calls)
        call_n_map=self.get_relatives_call_times_list(calls)
        res_map={}
        for c in contacts:
            if c.phone in self.lover_map and c.phone not in res_map:
                info={}
                info['phone']=c.phone
                info['name']=self.lover_map[c.phone]
                info['call_times']=c.phone in call_n_map and call_n_map[c.phone] or 0
                info['call_duration']=c.phone in call_d_map and call_d_map[c.phone] or 0
                info['location']=self.ext_api.get_phone_location(c.phone)
                reslist.append(info)
                res_map[c.phone]=1
        return  reslist

    def get_relatives_list(self,contacts,calls):
        reslist=[]
        call_d_map=self.get_relatives_call_duration_list(calls)
        call_n_map=self.get_relatives_call_times_list(calls)
        res_map={}
        for c in contacts:
            if c.phone in self.relative_map and c.phone not in res_map:
                info={}
                info['phone']=c.phone
                info['name']=c.name
                info['call_times']=c.phone in call_n_map and call_n_map[c.phone] or 0
                info['call_duration']=c.phone in call_d_map and call_d_map[c.phone] or 0
                info['location']=self.ext_api.get_phone_location(c.phone)
                reslist.append(info)
                res_map[c.phone]=1
        return  reslist

    def get_father_list(self,contacts,calls):
        reslist=[]
        call_d_map=self.get_parents_call_duration_list(calls)
        call_n_map=self.get_parents_call_times_list(calls)
        res_map={}
        for c in contacts:
            if c.phone in self.father_map and c.phone not in res_map:
                info={}
                info['phone']=c.phone
                info['name']=self.father_map[c.phone]
                info['call_times']=c.phone in call_n_map and call_n_map[c.phone] or 0
                info['call_duration']=c.phone in call_d_map and call_d_map[c.phone] or 0
                info['location']=self.ext_api.get_phone_location(c.phone)
                reslist.append(info)
                res_map[c.phone]=1
        return reslist

    def get_mather_list(self,contacts,calls):
        reslist=[]
        call_d_map=self.get_parents_call_duration_list(calls)
        call_n_map=self.get_parents_call_times_list(calls)
        res_map={}
        for c in contacts:
            if c.phone in self.mather_map and c.phone not in res_map:
                info={}
                info['phone']=c.phone
                info['name']=self.mather_map[c.phone]
                info['call_times']=c.phone in call_n_map and call_n_map[c.phone] or 0
                info['call_duration']=c.phone in call_d_map and call_d_map[c.phone] or 0
                info['location']=self.ext_api.get_phone_location(c.phone)
                reslist.append(info)
                res_map[c.phone]=1
        return reslist

    def get_home_list(self,contacts,calls):
        reslist=[]
        call_d_map=self.get_parents_call_duration_list(calls)
        call_n_map=self.get_parents_call_times_list(calls)
        res_map={}
        for c in contacts:
            if c.phone in self.home_map and c.phone not in res_map:
                info={}
                info['phone']=c.phone
                info['name']=self.home_map[c.phone]
                info['call_times']=c.phone in call_n_map and call_n_map[c.phone] or 0
                info['call_duration']=c.phone in call_d_map and call_d_map[c.phone] or 0
                info['location']=self.ext_api.get_phone_location(c.phone)
                reslist.append(info)
                res_map[c.phone]=1
        return reslist


    def get_parents_call_duration_list(self,calls):
        reslist=[]
        resmap={}
        for c in calls:
            if c.phone in self.m_f_map:
                if c.phone in resmap :
                    resmap[c.phone]+=c.calling_duration
                else:
                    resmap[c.phone]=c.calling_duration
        return resmap
        #for k,v in resmap.items():
        #        info={}
        #        info['phone']=k
        #        info['name']=self.m_f_map[k]
        #        info['calling_duration']=v
        #        info['location']=self.ext_api.get_phone_location(k)
        #        reslist.append(info)
        #return reslist

    def get_relatives_call_duration_list(self,calls):
        reslist=[]
        resmap={}
        lover_or_r_map=dict(self.relative_map,**self.lover_map)
        for c in calls:
            if c.phone in lover_or_r_map:
                if c.phone in resmap:
                    resmap[c.phone]+=c.calling_duration
                else:
                    resmap[c.phone]=c.calling_duration
        return resmap
        #for k,v in resmap.items():
        #        info={}
        #        info['phone']=k
        #        #info['name']=lover_or_r_map[k]
        #        info['calling_duration']=v
        #        info['location']=self.ext_api.get_phone_location(k)
        #        reslist.append(info)
        #return reslist

    def get_parents_call_times_list(self,calls):
        reslist=[]
        resmap={}
        for c in calls:
            if c.phone in self.m_f_map:
                if c.phone in resmap:
                    resmap[c.phone] +=1
                else:
                    resmap[c.phone] =1
        return resmap
        #for k,v in resmap.items():
        #    info={}
        #    info['phone']=k
        #    info['name']=self.m_f_map[k]
        #    info['call_times']=v
        #    info['location']=self.ext_api.get_phone_location(k)
        #    reslist.append(info)
        #return reslist

    def get_relatives_call_times_list(self,calls):
        reslist=[]
        resmap={}
        lover_or_r_map=dict(self.relative_map,**self.lover_map)
        for c in calls:
            if c.phone in lover_or_r_map:
                if c.phone in resmap:
                    resmap[c.phone] +=1
                else:
                    resmap[c.phone] =1
        return resmap
        #for k,v in resmap.items():
        #    info={}
        #    info['phone']=k
        #    info['name']=lover_or_r_map[k]
        #    info['call_times']=v
        #    info['location']=self.ext_api.get_phone_location(k)
        #    reslist.append(info)
        #return reslist

    def init_map(self,pre_contacts):
        ##smap={'':'通信录','0':'短信','1':'通话'}
        for c in pre_contacts:
            if is_m_f_blood(c.name,self.parent_list,self.parent_adj_list,self.parent_list_ch):
                if c.phone not in self.m_f_map:
                    self.m_f_map[c.phone]=c.name
                    if is_father(c.name,self.f_m_list[1]):
                        self.father_map[c.phone]=c.name
                    elif is_mather(c.name,self.f_m_list[0]):
                        self.mather_map[c.phone]=c.name
                    elif is_home(c.name):
                        self.home_map[c.phone]=c.name
            elif is_m_f_in_law(c.name,self.spouse_list):
                if c.phone not in self.relative_map:
                    self.relative_map[c.phone]=c.name
            elif is_uncle_aunt(c.name) or is_grandparent(c.name) or is_b_s(c.name):
                if c.phone not in self.relative_map:
                    self.relative_map[c.phone]=c.name
            elif is_spouse(c.name,self.spouse_list,self.spouse_adj_list):
                if c.phone not in self.lover_map:
                    self.lover_map[c.phone]=c.name
