#!/usr/bin/env python
# encoding: utf-8
import sys
import os
reload(sys)
from rules.models import BaseRule

class creditCard(BaseRule):
    def __init__(self):
        self.min_rule_map={
            60001:None,#职业
            60002:None,#信用额度
            60003:None,#当前可用信用额度
            60004:None,#近三个月内信用卡月还款金额
            60005:None,#三个月内月刷卡金额
            60006:None,#三个月内刷卡频次
            60007:None,#当前可用余额
            60008:None,#是否逾期记录（还款>30天）
            60009:None,#持卡人所在地去都市化程度
            60010:None,#三个月内消费金额>=8000元出现的次数
            60011:None,#公司所在地址是否与手机归属地一致
        }
	'''profession'''
    def get_profession(self,basedata):
        pass
    '''信用额度'''
    def get_all_credit_amount(self,basedata):
        pass
    '''当前可用额度'''
    def get_can_user_credit_amount_current(self,basedata):
        pass
    '''近三个月内信用卡月还款金额'''
    def get_repay_amount_before_3month(self):
        pass
    '''三个月内月刷卡金额'''
    def get_avg_amount_by_month(self):
        pass
    '''三个月内刷卡频次'''
    def get_times_of_thress_month(self):
        pass
    '''当前可用余额'''
    def get_left_over_amount(self,basedata):
        pass
    '''是否逾期记录（还款>30天）'''
    def get_repay_money_overdue_3month(self,basedata):
        pass
    '''持卡人所在地去都市化程度'''
    def credit_card_location(self,basedata):
        pass
    '''三个月内消费金额>=8000元出现的次数'''
    def get_most_amount_times(self,basedata):
        pass
    '''公司所在地址是否与手机归属地一致'''
    def company_address_same_with_phone_location(self,basedata):
        pass
    def get_score(self):
        pass


