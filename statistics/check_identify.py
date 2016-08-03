# coding=utf8
import sys
import os
import django
#sys.setdefaultencoding('utf8')
if __name__ == '__main__':
    local_dir = sys.argv[1]
    sys.path.append(local_dir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lycaon.settings'
    django.setup()
from django.conf import settings
from django.db.models import Q,Sum,F
from rules.models import BaseRule

from mongoengine import (
     StringField, ListField, IntField, Document, EmbeddedDocumentField, FloatField,
     DateTimeField, EmbeddedDocument
)
import logging
import StringIO
import json
logger = logging.getLogger('django.rules')
logger.setLevel(logging.INFO)
import time
from datetime import datetime, date, timedelta
from rules.base import get_right_datetime 
from rules.ruleset.post_loan_handler import PostLoanHandler
from rules.calculate import get_token
def get_time_now(hours=0,minutes=0,seconds=0):
    today=time.localtime();
    year=today.tm_year;
    month=today.tm_mon;
    day=today.tm_mday;
    return datetime(year,month,day,hours,minutes,seconds)

def check_id_info(token):
    rmap = get_token(token)
    idcard = rmap['idcard']
    user_reg_phone = rmap['user_phone']
    jd=rmap['jd']
    tb=rmap['tb']
    username=rmap['idinfo']['name']
    sp=rmap['sp']
    ucl=rmap['ucl']
    #自定义替换函数 mulsub
    ##################
    # x:字符串       #
    # i:替换开始位置 #
    # j:替换结束位置 #
    # stype:替换字符 #
    ##################
    mulsub=lambda x,i,j,s:x[:i] + ''.join(map( lambda it:it.replace(it,s),x[i:j] )) + x[j:]
    
    jd_judge_standard = mulsub(username,0,len(username)-1,'*')+'|'+mulsub(idcard,2,-4,'*')
    tb_judge_standard = mulsub(username,1,len(username),'*')+'|'+mulsub(idcard,1,-1,'*')
    sp_unicom_judge_standard = mulsub(username,0,0,'*')+'|'+idcard[:4]+'****'+idcard[-4:]
    #移动当前是x或*
    sp_mobile_judge_standard_1 = mulsub(username,1,-1,'*')
    sp_mobile_judge_stardard_2 = mulsub(username,0,len(username)-1,'x')

    jd_account_id = jd and jd.indentify_verified['detail'] or '-'
    tb_account_id = tb and tb.bindAccountInfo['identity'].replace('已认证','').replace(' ','') or '-'
    sp_account_id = sp and (sp.idcard and sp.real_name+'|'+sp.idcard or sp.real_name) or '-'

    #print 'jd----->',jd_account_id,'s---->',jd_judge_standard
    #print 'tb----->',tb_account_id,'s----->',tb_judge_standard
    #print 'sp----->',sp_account_id,'s------>',sp_unicom_judge_standard,'s1-->',sp_mobile_judge_standard_1,'s2-->',sp_mobile_judge_stardard_2

    #联通或移动
    sp_rs = sp_account_id==sp_unicom_judge_standard or sp_account_id==sp_mobile_judge_standard_1 or sp_account_id==sp_mobile_judge_stardard_2 or '-'

    return {
            'love_life':{
                'idcard' : idcard,
                'phone' : user_reg_phone,
                'result' : '-'
            },
            'jd_check':{
                'idcard' : jd_account_id,
                'phone' : jd and jd.phone_verifyied['detail'] or '-',
                'result' : len(jd_account_id)>=15 and (jd_account_id == jd_judge_standard) or '-'
            },
            'tb_check':{
                'idcard' : tb_account_id,
                'phone' : tb and tb.bindAccountInfo['bindMobile'] or '-',
                'result' : len(tb_account_id)>=15 and (tb_account_id==tb_judge_standard) or '-'
            },
            'sp_check':{
                'idcard' : sp_account_id,
                'phone' : sp and sp.phone_no or '-',
                'result' : sp_rs
            },
            'ucl_check':{
                'idcard' : '-',
                'phone' : '-',
                'result' : '-',
            }
    }



