#!/usr/bin/env python
# encoding: utf-8
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')
import requests
def is_black(idcard):
    url = "http://e.apix.cn/apixcredit/blacklist/dishonest"
    querystring = {"type":"your_value","name":"your_value","cardno":"your_value","phoneNo":"your_value","email":"your_value"}
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'apix-key': "您的apix-key"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response.text)
    
