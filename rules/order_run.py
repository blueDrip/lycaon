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

def cal_test():
    consumer = KafkaConsumer('event_deal',bootstrap_servers='101.200.193.228:9092,101.200.167.180:9092,123.56.249.148:9092')
    for message in consumer:
        print message.value
        if message:
            cal_by_message(message.value)
if __name__ == '__main__':
    print 'server start'
    while True:
        cal_test()
