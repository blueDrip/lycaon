#!/usr/bin/env python
# encoding: utf-8
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')
from rules.models import BaseRule
class Tbao(BaseRule):
	def __init__(self):
		self.min_rule_map={
            40001:None,#淘宝授权
            40002:None,#淘宝消费金额
            40003:None,#淘宝消费次数
            40004:None,#淘宝登陆频次
        }
	'''实名认证'''
	def is_valid_name(self,basedata):
		pass
	def is_valid_phone(self,basedata):
		pass
	def get_huiyuanjibie(self,basedata):
		pass
	def get_three_month_before_consume(self):
		pass
	def get_three_month_after_consume(self):
		pass
	def get_laster_login_time_inter(self):
		pass
	def get_address(self,basedata):
		pass
