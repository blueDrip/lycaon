#!/usr/bin/env python
# encoding: utf-8
import sys
import os
from rules.models import BaseRule
from rules.raw_data import minRule
class PersonInfo(BaseRule):
    def __init__(self,basedata):
        pass
    #验证是否本人 ps 1:身份验证通过,
    def base_line(self,basedata):
        is_pass = basedata.user and basedata.user.is_certification or 0
        self.chef_map={'身份验证':is_pass and '通过' or '未通过'}
        #if not is_pass:
        #    basedata.user=None        
        #    self.is_chef='未通过'
        #    self.is_chef_item='身份验证'
        #else:
        #    pass
    def load_rule_data(self,basedata):
        self.min_rule_map={
            10001:self.get_age(basedata),
            10002:self.get_sex(basedata),
            10003:self.get_edu(basedata),
            10004:self.get_residenza(basedata), 
            10005:self.get_marry_status(basedata),
            10006:self.get_profession(basedata),
            10007:self.is_samephoto_with_idcard(basedata)
        }
    def get_age(self,basedata):
        r = minRule()
        age = basedata.idcard_info['age']
        r.source=str(age)
        r.score = 10
        if u'unknow' == age:
            r.score = 10
        elif age<=18:
            r.score=10
        elif age>18 or age<=25:
            r.score=70
        elif age>25 and age<=40:
            r.score=100
        elif age>40:
            r.score=70
        r.value = str(age)+u'岁;出生年月日:'+basedata.idcard_info['birthday']
        r.feature_val=str(age)+u'岁'
        r.name=u'年龄'
        return r
    def get_sex(self,basedata):
        sex = basedata.idcard_info['sex']
        r=minRule()
        r.source=sex
        r.score = 10
        r.value=sex
        if sex==u'男':
            r.score=80
        elif sex==u'女':
            r.score=100
        r.name=u'性别'
        r.feature_val = sex
        return r

    def get_edu(self,basedata):
        edu=basedata.user and basedata.user.education or 'unknow'
        r = minRule()
        r.value=edu
        r.source=edu
        r.name=u'教育程度'
        r.score=10
        if edu in u'中专/高中及一下':
            r.score = 50
        elif edu in u'专科':
            r.score = 70
        elif edu in u'本科':
            r.score = 90
        elif edu in u'硕士及以上':
            r.score = 100
        r.feature_val = edu
        return r
    def get_residenza(self,basedata):
        home_location=basedata.home_location
        r=minRule() 
        r.value=home_location
        r.name=u'老家住址(市/县)'
        r.score = 10
        if u'县' in home_location:
            r.score = 70
            r.source=u'县'
        elif u'市' in home_location:
            r.score = 100
            r.source=u'市'
        r.feature_val = home_location
        return r
    def get_marry_status(self,basedata):
        r=minRule()
        marr = basedata.user and basedata.user.marry_info or 'unknow'
        r.value = marr
        r.name=u'是否结婚'
        r.source = marr
        r.score = 10
        if u'unknow' == marr:
            r.score = 10
            r.feature_val = marr
        elif u'未婚' in marr:
            r.score = 70
            r.feature_val = u'未婚' 
        elif u'已婚，无子女' in marr:
            r.score = 90
            r.feature_val = u'已婚，无子女'
        elif u'已婚，有子女' in marr:
            r.score = 100
            r.feature_val = u'已婚，有子女'
        elif u'离异' in marr:
            r.score = 60
            r.feature_val = u'离异'
        elif u'丧偶' in marr:
            r.score = 80
            r.feature_val = u'丧妻'
        return r

    def get_profession(self,basedata):
        p = basedata.user and basedata.user.profession or 'unknow'
        r=minRule()
        r.value = p
        r.score=10
        if p == u'企业主':
            r.score = 90
        elif p == u'上班族':
            r.score = 80
        elif p == u'自由职业':
            r.score = 60
        elif p == u'学生':
            r.score = 70
        elif p == u'其他':
            r.score = 50
        r.name=u'职业'
        r.source = p
        r.feature_val = p
        return r
    def is_samephoto_with_idcard(self,basedata):
        idsame = basedata.user and basedata.user.is_certification or 'unknow'
        r=minRule()
        r.score = 10
        r.name=u'是否身份验证'
        if idsame==1:
            r.value = u'验证通过'
            r.score = 100
        elif idsame ==0:
            r.value = u'未通过'
            r.score = 10
        r.source = str(idsame)
        r.feature_val = r.value
        return r

    def get_score(self):
        min_rule_map = self.min_rule_map
        age_score=min_rule_map[10001].score*0.2
        sex_score=min_rule_map[10002].score*0.2
        edu_score=min_rule_map[10003].score*0.1
        residenza_score=min_rule_map[10004].score*0.2
        profession_score=min_rule_map[10006].score*0.1
        phone_score=min_rule_map[10007].score*0.2
        score=age_score+sex_score+edu_score+profession_score+phone_score+residenza_score
        return score
