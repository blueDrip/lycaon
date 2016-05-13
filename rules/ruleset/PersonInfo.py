#!/usr/bin/env python
# encoding: utf-8
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')
from rules.models import BaseRule
from rules.raw_data import minRule
class PersonInfo(BaseRule):
    def __init__(self,basedata):
        self.min_rule_map={
            10001:self.get_age(basedata),
            10002:self.get_sex(basedata),
            10003:self.get_edu(basedata),
            10004:self.get_residenza(), 
            10005:self.get_marry_status(),
            10006:self.is_black(),
            10007:self.get_profession(),
            10008:self.is_samephoto_with_idcard()
        }    

    def get_age(self,basedata):
        r = minRule()
        age=basedata.user and basedata.user.age or 18
        r.source=str(age)
        if age<=18:
            r.score=10
        elif age>18 or age<=25:
            r.score=70
        elif age>25 and age<=40:
            r.score=100
        elif age>40:
            r.score=70
        r.value=str(age)+'岁'
        r.name=u'年龄'
        return r
    def get_sex(self,basedata):
        sex=basedata.user and basedata.user.sex or 'unknow'
        r=minRule()
        r.source=sex
        r.score=0
        r.value=sex
        if sex==u'男':
            r.score=80
        elif sex==u'女':
            r.score=100
        r.name=u'性别'
        return r

    def get_edu(self,basedata):
        edu=basedata.user and basedata.user.edu or 'unknow'
        r = minRule()
        r.value=edu
        r.source=edu
        r.name=u'教育程度'
        r.score=0
        if edu==u'本科':
            r.score=80
        elif edu in [u'研究生',u'博士']:
            r.score=100
        elif edu==u'高中':
            r.score=60
        elif edu==u'初中':
            r.score=40
        return r
    def get_residenza(self):
        r=minRule()
        r.value=u''
        r.name=u'住址'
        r.source=u'县'
        r.score=30
        return r
    def get_marry_status(self):
        r=minRule()
        r.value=u'结婚'
        r.name=u'是否结婚'
        r.source=u'结婚'
        r.score=0
        return r
    def is_black(self):
        r=minRule()
        r.value=u'非黑名单'
        r.name=u'是否黑名单'
        r.score=100
        r.source=u'是'
        return r
    def get_profession(self):
        r=minRule()
        r.value=u'老师' 
        r.name=u'职业'
        r.score=100
        r.source=u'待定'
        return r
    def is_samephoto_with_idcard(self):
        r=minRule()
        r.value=u'相同'
        r.name=u'身份证照片是否一致'
        r.score=100
        r.source=u'相同'
        return r
    def get_score(self):
        min_rule_map = self.min_rule_map
        age_score=min_rule_map[10001].score*0.2
        sex_score=min_rule_map[10002].score*0.2
        edu_score=min_rule_map[10003].score*0.1
        residenza_score=min_rule_map[10004].score*0.2
        profession_score=min_rule_map[10007].score*0.2
        phone_score=min_rule_map[10008].score*0.1
        score=age_score+sex_score+edu_score+profession_score+phone_score+residenza_score
        return score
    
