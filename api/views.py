# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse
from rules.models import BaseRule
from rules.ruleset.JD import JD
from rules.ruleset.PersonInfo import PersonInfo
from rules.base import BaseData
from rules.ruleset.Sp import Sp
from api.models import Profile
from rules.raw_data import UserContact,topResult
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt
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

def credit_detail(request):
    uid=request.GET['uid']
    top_rs = topResult.objects.filter(user_id = uid).order_by('-created_time').first()
    return render(request, 'api/detail.html', {'tp': top_rs})

def users_views(request):
    ulist = Profile.objects.all()
    return render(request,'api/users.html',{'users':ulist})
