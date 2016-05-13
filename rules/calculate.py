#!/usr/bin/env python
# encoding: utf-8

import traceback
import socket
import time
import urllib
import datetime

import logging
from rules.raw_data import jingdong
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
    for k,v in b.min_rule_map.items():
        print k,v.name,'\t',v.feature_val
        print '>>>>>>>>>>>>',v.value.replace('\t','\n')
    print '>>>>>>>>>>>>>>>>得分:',b.get_score()
    b=PersonInfo(bd)    
    for k,v in b.min_rule_map.items():
        print k,v.name,'\t',v.feature_val
        print '>>>>>>>>>>>>>>>',v.value.replace('\t','\n')
    print '>>>>>>>>>>>>>>>>得分:',b.get_score()
    b=Sp(bd)
    for k,v in b.min_rule_map.items():
        print k,v.name,'\t',v.feature_val
        print '>>>>>>>>>>>>>>>>',v.value.replace('\t','\n')
    print '>>>>>>>>>>>>>>>得分:',b.get_score()
    b=PostLoanNewRule(bd)
    for k,v in b.min_rule_map.items():
        print k,v.name,'\t',v.feature_val
        print '>>>>>>>>>>>>>>>>',v.value.replace('\t','\n')
    print '>>>>>>>>>>>>>>>得分:',b.get_score()


