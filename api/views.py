# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from rules.models import BaseRule
from rules.ruleset.JD import JD
from rules.ruleset.PersonInfo import PersonInfo
from rules.base import BaseData
from rules.ruleset.Sp import Sp
from api.models import Profile,ucredit,Busers
from rules.raw_data import UserContact,topResult
from datetime import datetime
from statistics.models import RulesInfo
from rules.calculate import cal_by_message
from django.views.decorators.csrf import csrf_exempt
from api.models import adminAccount
from api.sys import apache
import binascii
import json
import logging
import time
import requests
import calendar
logger = logging.getLogger('django.api')
logger.setLevel(logging.INFO)

def index(request):
    '''    
    b=BaseRule()
    try:
        bd=BaseData('')
        b=PersonInfo(bd)
        q=Question.objects.filter()[1]
        q=q.question_text
        ss=q
        for k,v in b.min_rule_map.items():
            ss+=str(k)+';'+v.name+';'+v.value+';'+str(v.score)
        logger.info('aaa')
        logger.error('error occurs')
        return HttpResponse(ss)
    except Exception as e:
        logger.info(e)
        return HttpResponse(e)
    '''
    return HttpResponse('sdfdsf')

def score_views(request):
    token = request.GET['token']
    try:
        if token:
            score = cal_by_message(token)
            #if score:
            #    return HttpResponse(json.dumps({'user_score':score}))
            return HttpResponse(json.dumps({'user_score':score}))
        return HttpResponse(json.dumps({'user_score':-3}))
    except:
        return HttpResponse(json.dumps({'user_score':-3}))

def credit_detail(request):
    uid=request.GET['uid']
    top_rs = topResult.objects.filter(user_id = uid).order_by('-created_time').first()
    return render(request, 'api/detail.html', {'tp': top_rs})

def users_views(request):
    ulist = Profile.objects.using('users').all()
    return render(request,'api/users.html',{'users':ulist})
def rules_detail_info(request):
    uid=request.GET['uid']
    rs = RulesInfo.objects.filter(user_id=uid).order_by('-created_at').first()
    return render(request, 'api/detailinfo.html', {'rs': rs})

def delitem(request):
    uid=request.GET['uid'].lower()
    user_id = binascii.a2b_hex(uid)
    Profile.objects.using('users').filter(user_id=user_id).delete()
    Busers.objects.using('users').filter(user_id=user_id).delete()
    ucredit.objects.using('users').filter(user_id=user_id).delete()
    
    #ulist = Profile.objects.using('users').all()
    #return render(request,'api/users.html',{'users':ulist})
    return HttpResponseRedirect('/apix/userinfo/')  #跳转到index界面


'''数据分析admin'''
#首页
def admin_login_views(request):
    return render(request,'admin/login.html')
def login_auth(request):
    username=request.POST['username']
    pwd=request.POST['passwd']
    m=adminAccount.objects.using('admin').filter(login_name=username,pwd=pwd)
    if m:
        request.session['user']=m.first().login_name
        #设置过期时间
        #request.session.set_expiry(100)
    return HttpResponseRedirect('/apix/chars/')    
def logout(request):
    request.session.flush()
    return HttpResponseRedirect('/apix/login/')

def admin_index_views(request):
    ulist = Profile.objects.using('users').all()
    return render(request,'admin/index.html',{'users':ulist})
#误差
def check_error_views(request):
    return render(request,'admin/checkerr.html')
#数据统计
def stat_data_views(request):
    return render(request,'admin/statdata.html')
#特征选择
def choice_feature_views(request):
    return render(request,'admin/feturesinfo.html')
#模型迭代
def cal_again_views(request):
    return render(request,'admin/models.html')
#系统设置
def set_sys_views(request):
    return render(request,'admin/sys.html')

def apache_views(request):
    return HttpResponse(apache())

#权限设置
def role_views(request):
    return render(request,'admin/userRole.html')
#规则
def rules_items_vies(request):
    uid=request.GET['uid']
    top_rs = topResult.objects.filter(user_id = uid).order_by('-created_time').first()
    return render(request, 'admin/rules.html', {'tp': top_rs})
#删除
def del_views(request):
    uid=request.GET['uid'].lower()
    user_id = binascii.a2b_hex(uid)
    Profile.objects.using('users').filter(user_id=user_id).delete()
    Busers.objects.using('users').filter(user_id=user_id).delete()
    ucredit.objects.using('users').filter(user_id=user_id).delete()    
    return HttpResponseRedirect('/apix/index/')
#数据统计
def stat_chars_views(request):
    return render(request,'admin/chars.html',{'year':datetime.now().year,'month':datetime.now().month })

def reg(request):
    year = request.GET['year']
    month = request.GET['month']
    url = "http://123.56.93.103:3000/user/number"
    querystring = { "year":year,"month":int(month)<10 and '0'+ month or month }
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    result_map = json.loads(response.text)['result']
    month_days = calendar.monthrange(int(year),int(month))[1]
    rs={}
    for i in range(1,month_days+1):
        key=str(datetime(int(year),int(month),i).date())
        rs[i]=key in result_map and result_map[key] or 0

    return HttpResponse(
            json.dumps({'d1':{'year':year,'month':month },
                'rs' : rs
            })

        )
def reback(request):
    year=request.GET['year']
    month=request.GET['month']
    return HttpResponse(
            json.dumps({'d1':{'year':year,'month':month},
                'rs' : {
                    1 : 0,
                    2 : 1,
                    3 : 4,
                    4 : 7,
                    5 : 8,
                    6 : 9,
                    7 : 8,
                    8 : 8,
                    9 : 9,
                    10 : 6,
                    11 : 10,
                    12 : 7,
                    13 : 6,
                    14 : 7,
                    15 : 8,
                    16 : 9,
                    17 : 8,
                    18 : 8,
                    19 : 9,
                    20 : 6,
                    21 : 8,
                    22 : 11,
                    23 : 4,
                    24 : 7,
                    25 : 8,
                    26 : 9,
                    27 :8,
                    28 :8,
                    29 :9
            }
            })

        )
