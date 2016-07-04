#!/usr/bin/env python
# encoding: utf-8
import sys
import os
import django
import logging
import time
if __name__ == '__main__':
    local_dir = sys.argv[1]
    sys.path.append(local_dir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lycaon.settings'
    django.setup()
from django.conf import settings
from datetime import datetime,timedelta
from rules.util.sms_email import MyEmail

#时刻检查日志错误
def rules_log():
    st=datetime.now().date()
    count = 0
    for line in open(settings.LOG_DIR+'rules.log','r'):        
        if str(st) in line:
            count+=1
    return count

def rules_content_log():
    st=datetime.now().date()
    value = '' 
    for line in open(settings.LOG_DIR+'rules.log','r'):        
        if str(st) in line:
            value+=line
    return value
if __name__=='__main__':
    cstr = rules_content_log()
    st = datetime
    my = MyEmail(cstr)
    my.user = "1049787469@qq.com"
    my.passwd = "abcd1243"
    my.to_list = ["1049787469@qq.com"]
    my.cc_list = [""]
    my.tag = "规则出现bug"
    my.send()
