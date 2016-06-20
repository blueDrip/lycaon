#coding:utf8
from django.test import TestCase

# Create your tests here.
from rules.orm import *
from rules.base import BaseData
from rules.ruleset.Tbao import Tbao
def tt():
    cn=[{"taobao_name" : '石头买买2' },
        {"taobao_name" : 'tb122917_00' },
        {"taobao_name" : '15201468346' },
        {"taobao_name" : 'xiaoertianya9'},
        {"taobao_name" : '15313349378'},
        {"taobao_name" : 'apiplus@126.com' },
        {"taobao_name" : 'tb122917_00' },
        {"taobao_name" : '石头买买2' }
    ]
    for it in cn:
        tt=tb_orm(cnd=it)
        bd=BaseData({'user':None,
            'user_id':'None',
            'idcard':None,
            'sp':None,
            'cb':None,
            'jd':None,
            'ucl':None,
            'tb':tt,
            'user_phone':'15600300721'
        })
        tb=Tbao(bd)
        print tb.get_score()
