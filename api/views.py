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
import binascii
import json
import logging
logger = logging.getLogger('django.api')
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
def admin_login_views(request):
    return render(request,'admin/login.html')

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
    return render(request,'admin/chars.html')

def test(request):
    return render(request,'api/tt.html',{'v':'sssssssss'})
