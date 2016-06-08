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
from rules.calculate import cal_by_message
from kafka import KafkaConsumer
from datetime import datetime
cal_logger = logging.getLogger('django.cal')
cal_logger.setLevel(logging.INFO)

def daemonize(stdin='/dev/null',stdout= '/dev/null', stderr= 'dev/null'):
    '''Fork当前进程为守护进程，重定向标准文件描述符
        （默认情况下定向到/dev/null）
    '''
    #Perform first fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)  #first parent out
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" %(e.errno, e.strerror))
        sys.exit(1)

    #从母体环境脱离
    os.chdir("/")
    os.umask(0)
    os.setsid()
    #执行第二次fork
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0) #second parent out
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %s]n" %(e.errno,e.strerror))
        sys.exit(1)

    #进程已经是守护进程了，重定向标准文件描述符
    for f in sys.stdout, sys.stderr: f.flush()
    si = file(stdin, 'r')
    so = file(stdout,'a+')
    se = file(stderr,'a+',0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def example_main():
    #sys.stdout.write('Daemon started with pid %d\n' % os.getpid())
    #sys.stdout.write('Daemon stdout output\n')
    #sys.stderr.write('Daemon stderr output\n')
    consumer = KafkaConsumer('event_deal',bootstrap_servers='101.200.193.228:9092,101.200.167.180:9092,123.56.249.148:9092')
    for message in consumer:
        #print message.value
        if message:
            try:
                cal_by_message(message.value)
            except:
                continue

        sys.stdout.write('【　conusmer an message　】'+'\n')
        sys.stdout.flush()
if __name__ == "__main__":
    daemonize('/dev/null','/home/sw/logs/lycaon/calculate.log','home/sw/logs/daemon.log')
    example_main()

