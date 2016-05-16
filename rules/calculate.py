#!/usr/bin/env python
# encoding: utf-8

import traceback
import socket
import time
import urllib
import datetime

import logging
from rules.raw_data import topResult,DetailRule
from rules.ruleset.JD import JD
from rules.ruleset.PersonInfo import PersonInfo
from rules.ruleset.Sp import Sp
from rules.ruleset.postloan import PostLoanNewRule
from rules.models import BaseRule
from rules.base import BaseData

'''调用之前进行黑名单验证'''
def is_black():
    pass
'''
满足基本的条件
1.通讯录长度>30
2.通话记录（手机上传的）>30
3.不是中介
'''
def is_basic():
    pass
def cal():
 
    #if is_black or is_basic
    #    return '黑名单'
    b=BaseRule()
    bd=BaseData('')
    b=JD(bd)
    tp_rs = topResult()

    print '>>>>>>>>>>>>>>>>个人信息'
    dl=[]
    Dr_p=DetailRule()
    b=PersonInfo(bd)
    for k,v in b.min_rule_map.items():
        v.ruleid = str(k)
        v.value = v.value.replace('\t','<br/>')
        v.save()
        dl.append(v)
    Dr_p.name=u'个人信息'
    Dr_p.rule_id=1
    Dr_p.score=int(b.get_score())
    Dr_p.rules=dl
    Dr_p.save()

    print '>>>>>>>>>>>>>京东'
    Dr_jd=DetailRule()
    dl=[]
    b = JD(bd)
    for k,v in b.min_rule_map.items():
        v.ruleid = str(k)
        v.value = v.value.replace('\t','<br/>')
        v.save()
        dl.append(v)
    Dr_jd.name=u'京东'
    Dr_jd.score=int(b.get_score())
    Dr_jd.rules=dl
    Dr_jd.rule_id=2
    Dr_jd.save()

    print '>>>>>>>>>>>>>>>>>运营商'
    dl=[]
    b=Sp(bd)
    Dr_sp=DetailRule()
    for k,v in b.min_rule_map.items():
        v.ruleid = str(k)
        v.value = v.value.replace('\t','<br/>')
        v.save()
        dl.append(v)

    Dr_sp.name=u'运营商'
    Dr_sp.rule_id=3
    Dr_sp.score=int(b.get_score())
    Dr_sp.rules=dl
    Dr_sp.save()

    print '>>>>>>>>>>>>>>>>>贷后'
    b=PostLoanNewRule(bd)
    Dr_post=DetailRule()
    dl=[]
    for k,v in b.min_rule_map.items():
        v.ruleid=str(k)        
        v.value = v.value.replace('\t','<br/>')
        v.ruleid = str(k)
        v.save()
        dl.append(v)
    print 'success'
    Dr_post.name=u'贷后'
    Dr_post.rule_id=4
    Dr_post.score=int(b.get_score())
    Dr_post.rules=dl
    Dr_post.save()

    print '>>>>>>>>>>>>>>bank'
    

    tp_rs.name = u'credit_score'
    tp_rs.score=100
    tp_rs.rulelist=[Dr_p,Dr_jd,Dr_sp,Dr_post]
    tp_rs.save()
    print 'successful!'

