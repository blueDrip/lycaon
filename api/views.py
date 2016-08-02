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
from rules.calculate import cal_by_message,desplay_detail_data
from django.views.decorators.csrf import csrf_exempt
from api.models import adminAccount,privaliage,role,privaliage_role,user_role
from sole_models.statistics.china_mobile import get_cb_infos
from sole_models.statistics.china_union import get_um_info
from sole_models.sole_orm import china_unicom_orm_desplay,china_mobile_orm_desplay
from rules.ext_api import EXT_API
from api.sys import apache
from rules.check_log import rules_log
from rules.util.utils import get_tb_info
from rules.ext_api import EXT_API
import binascii
import json
import logging
import time
import requests
import calendar
logger = logging.getLogger('django.api')
logger.setLevel(logging.INFO)
other = logging.getLogger('django.others')
other.setLevel(logging.INFO)
ext_api = EXT_API()
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
            if score:
                return HttpResponse(json.dumps({'user_score' : score}))
        return HttpResponse(json.dumps({'user_score':-3}))
    except:
        return HttpResponse(json.dumps({'user_score':-3}))

#sp数据
def sp_data_views(request):
    if 'token' not in request.GET or 'phone' not in request.GET:
        return HttpResponse(json.dumps({'err':'token or phone is must'}))
    try:
        token=request.GET['token']
        phone=request.GET['phone']
        ext_api=EXT_API()
        ptype=ext_api.get_phone_location(phone) or {'supplier':'none'}
        if token and phone:
            cnd = {'token':token}
            rs={'note':'unknown'}
            if '移动' in ptype['supplier']:
                cc=china_mobile_orm_desplay(cnd)
                rs=get_cb_infos(cc)            
            elif '联通' in ptype['supplier']:
                cc=china_unicom_orm_desplay(cnd)
                rs=get_um_info(cc)
            else:
                rs={'notice':'the phone type is not supported!'}
            return HttpResponse(json.dumps(rs))
        return HttpResponse("error! token or phone is empty!")
    except:
        return HttpResponse("an error occured")


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

def save_event(request):
    token=request.GET['token']
    try:
        other.info("Save_to_Mongo"+'  '+token)
        start=time.clock()
        rs = desplay_detail_data(token,exapi=ext_api)
        end=time.clock()
        other.info("cal time is :===============> "+str(end-start))
        if rs==-1:
            return HttpResponse('{"code":1,msg:"数据正在抓取中"}')
        elif rs==1:
            return HttpResponse('{"code":0,msg:"success"}')
        else:
            pass
    except:
        other.error(get_tb_info()+"Save_to_Mongo"+'  '+token)
        return  HttpResponse('{"code":-1,msg:"error"}')

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
        #权限查询
        role_id=user_role.objects.using('admin').filter(uid=m.first().id).first().rid
        r = role.objects.using('admin').filter(rid=role_id).first()
        pr=privaliage_role.objects.using('admin').filter(role_id = r.rid)
        pl=privaliage.objects.using('admin').filter(privaliage_id__in=[p.privaliage_id for p in pr])
        request.session['admin_level'] = r.descname
        request.session['privaliage'] = [{'pid':it.privaliage_id,
            'url':it.url,
            'privaliage_name':it.privaliage_name } for it in pl ]

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

#日志检查
def check_log(request):
    count = rules_log()
    st = str(datetime.now().date())
    dt = str(datetime.now())
    return HttpResponse(json.dumps({'st':str(st),'dt':str(dt),'err_count':count}))
#重启apache
def apache_views(request):
    return HttpResponse(apache())

#权限设置
def role_views(request):
    u=adminAccount.objects.using('admin').all()
    p = privaliage.objects.using('admin').all()
    r = role.objects.using('admin').all()
    return render(request,'admin/userRole.html',{'adminusers':u,'prlist':p,'r':r})




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


#创建用户
@csrf_exempt
def create_user_views(request):
    uname = request.POST['name']
    pwd = request.POST['pwd']
    a=adminAccount.objects.using('admin').filter(login_name=uname)
    if a:
        return HttpResponse(json.dumps({'notnull':-3}))
    if not uname:
        return HttpResponse(json.dumps({'notnull':-2}))
    elif not pwd:
        return HttpResponse(json.dumps({'notnull':-1}))
    
    a=adminAccount()
    a.login_name = uname
    a.pwd = pwd
    a.login_time = datetime.now()
    a.save(using='admin')
    return HttpResponse(json.dumps({
        'id' : str(a.id),
        'login_name' : uname,
        'ip' : str('192.168.1.120'),
        'login_time' : str(a.login_time)
    }))
#角色
def chagerole(request):
    rid = request.GET['rid']
    pr=privaliage_role.objects.using('admin').filter(role_id = int(rid))
    pl=privaliage.objects.using('admin').filter(privaliage_id__in=[p.privaliage_id for p in pr])
    return HttpResponse(json.dumps({'privaliage_id_list':[it.privaliage_id for it in pl]}))
#删除系统管理员
def del_sys_user(request):
    uid = request.GET['uid']
    #系统管理员admin,不能删除
    if int(uid) !=1:
        m=adminAccount.objects.using('admin').filter(id=int(uid)).delete()
    return HttpResponseRedirect('/apix/role/')
 
#创建角色
def create_role(request):
    rolename = request.GET['rolename']
    check_list = request.GET['privaliage_list']
    if not rolename or not check_list:
        return HttpResponse(json.dumps({'notnull':0}))
    r=role.objects.using('admin').filter(descname=rolename)
    if r:
        return HttpResponse(json.dumps({'notnull':-1}))
    r=role()
    r.descname=rolename
    r.save(using='admin')
    #分配权限
    rid=r.rid
    if check_list:
        prolist=[]
        for pid in check_list.strip('c').split('c'):
            pr= privaliage_role()
            pr.role_id = rid
            pr.privaliage_id = int(pid)
            prolist.append(pr)
            #pr.save(using='admin')
        #批量插入
        privaliage_role.objects.using('admin').bulk_create(prolist)
    return HttpResponse(json.dumps({'rolename':r.descname,'rid':r.rid}))
#分配角色
def distr_role_to_user(request):
    uid = request.GET['uid']
    rid = request.GET['rid']
    if int(rid)<0:
        return HttpResponse(0)
    ru = user_role()
    ru.uid = int(uid)
    ru.rid = int(rid)
    ru.save(using='admin')
    return HttpResponse(1)

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
