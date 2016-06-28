# coding=utf8

import traceback
import logging
from django.http import QueryDict, JsonResponse
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import SESSION_KEY    
from urllib import quote
base_logger = logging.getLogger('django.api')
base_logger.setLevel(logging.INFO)    

class QtsAuthenticationMiddleware(object):    
    def process_request(self, request):   
        #base_logger.info(request.path)
        #if "username" not in request.session:
        #    request.session['username'] = 'sw'
        #    return render(request,'admin/login.html')       
        #base_logger.info('00000000000'+request.session["username"]+str(request.session.get_expiry_age()))
        '''不拦截首页访问和登陆过程'''
        base_logger.info(str(request.session.keys())+'sssssssssssssss\t'+str('sss' in request.session))
        if '/apix/score/' in request.path:
            return None
        if 'user' not in request.session and  request.path not in  ['/apix/login/','/apix/login_auth/']:
            return HttpResponseRedirect('/apix/login/')
        return None
