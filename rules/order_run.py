#!/usr/bin/env python
# encoding: utf-8
import sys
import os
import django
import logging
if __name__ == '__main__':
    local_dir = sys.argv[1]
    sys.path.append(local_dir)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lycaon.settings'
    django.setup()
from django.conf import settings
from rules.calculate import cal_by_message
from kafka import KafkaConsumer
cal_logger = logging.getLogger('django.cal')
cal_logger.setLevel(logging.INFO)

def createDaemon():    
    # create - fork 1
    try:
        if os.fork()>0:
            os._exit(0)
    except OSError, error:
        print 'fork #1 failed: %d (%s)' % (error.errno, error.strerror)
        os._exit(1)
        # it separates the son from the father
    os.chdir('/')
    os.setsid()
    os.umask(0) 
    # create - fork 2
    try:
        pid = os.fork()
        if pid>0:
            print 'Daemon PID %d'%pid
            os._exit(0)
    except OSError, error:
        print 'fork #2 failed: %d (%s)' % (error.errno, error.strerror)
        os._exit(1)
    funzioneDemo() # function demo
def funzioneDemo():
    consumer = KafkaConsumer('event_deal',bootstrap_servers='101.200.193.228:9092,101.200.167.180:9092,123.56.249.148:9092')
    for message in consumer:
        print message.value
        if message:
            cal_by_message(message.value)
if __name__ == '__main__':
    print 'server start'
    createDaemon()
