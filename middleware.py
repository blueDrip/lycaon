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
        base_logger.info(request.session.keys())
        '''不拦截首页访问和登陆过程'''
        not_auth_list=['/apix/score/','/apix/spinfo/','/apix/saveitem/','/apix/checkbase/']
        if request.path in not_auth_list:
            return None
        if 'user' not in request.session and  request.path not in  ['/apix/login/','/apix/login_auth/']:
            return HttpResponseRedirect('/apix/login/')
        elif 'privaliage' in request.session:
            url_list = [ it['url'] for it in request.session['privaliage'] ]

            url_list.append('/apix/chars/')

            url_list.append('/apix/login/')
            url_list.append('/apix/login_auth/')

            url_list.append('/apix/reg/')
            url_list.append('/apix/reback/')
            url_list.append('/apix/apache/')
            url_list.append('/apix/ruleitems/')
            url_list.append('/apix/rulesinfo/')
            url_list.append('/apix/deluser/')
            url_list.append('/apix/createuser/')
            url_list.append('/apix/createrole/')
            url_list.append('/apix/distrrole/')
            url_list.append('/apix/logout/')                      
            url_list.append('/apix/chagerole/')
            url_list.append('/apix/delsysuser/')
            url_list.append('/apix/checklog/')
            base_logger.info(url_list)
            #没有权限访问其他路径,跳到首页
            if request.path not in url_list:
                return HttpResponseRedirect(url_list[0])
        return None
