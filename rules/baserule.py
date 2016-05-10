# coding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
# Create your models here.
import datetime
import traceback
from django.db import models
from django.conf import settings
from rules.raw_data import minRule
class BaseRule:
    def __init__(self):
        self.min_rule_map={}
        self.minrule = minRule()
    def get_score(self):
        return
