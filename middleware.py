# coding=utf8

import traceback
import logging
from django.http import QueryDict, JsonResponse
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import SESSION_KEY    
from urllib import quote
base_logger = logging.getLogger('django.rules')
base_logger.setLevel(logging.INFO)    

class QtsAuthenticationMiddleware(object):    
    def process_request(self, request):   
        #base_logger.info(request.path)
        #if "username" not in request.session:
        #    request.session['username'] = 'sw'
        #    return render(request,'admin/login.html')       
        #base_logger.info('00000000000'+request.session["username"]+str(request.session.get_expiry_age()))
        return None
