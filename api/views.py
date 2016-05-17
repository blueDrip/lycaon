# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse
from rules.models import BaseRule
from rules.ruleset.JD import JD
from rules.ruleset.PersonInfo import PersonInfo
from rules.base import BaseData
from rules.ruleset.Sp import Sp
#from api.models import Question
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
@csrf_exempt
def get_usercontact(request):
    if  request.method == 'POST':
        req=''
        conlist = []
        try:

            req = json.loads(request.body)
            conlist = eval(req['linkmen'])

        except:
            return HttpResponse('json格式错误')
        clist=[]
        for itt in conlist:
            u = UserContact()
            u.name=itt['name']
            u.owner_phone=req["phone"]
            u.device_id = req["device_id"]
            u.source = str(itt['source'])
            u.created_at = datetime.now()
            u.phone = itt['contact_phone']
            u.phone_location=''
            u.call_count = 0
            clist.append(u)
        u = UserContact.create_contacts(clist)
        if u:
            logger.info('success')
            return HttpResponse({'ok'})
        return HttpResponse('an error happend!')
    if request.method == 'GET':
        return HttpResponse(request.GET['name'])

def credit_detail(request):
    top_rs = topResult.objects.filter().first()
    return render(request, 'api/detail.html', {'tp': top_rs})
