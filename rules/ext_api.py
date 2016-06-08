#!/usr/bin/env python
# encoding: utf-8
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')
homedir = os.getcwd()

sys.path.append(homedir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'lycaon.settings'
from django.conf import settings

import socket
import time
import urllib
import math
import json
import re
import requests
#from rules.base import *
#固话归属地的文件
tel_file = None
phone_file = settings.PHONE_FILE
id_location_file = settings.ID_FILE
import logging
#base_logger = logging.getLogger('django.rules')
#base_logger.setLevel(logging.INFO)

def judge(identifice):
    for line in open(id_location_file,"r"):
        flist = line.strip().split('\t')
        if len(flist) < 3:
            continue
        id=identifice[0:6];
        ##print id,flist[1]
        if id==flist[1]:
            #print "xxxx",flist[2]
            return flist[2]
            #return getArea(line[7:]);
    #调用api
    key='c9323635da814c6eeba0814fecfaf7be';
    url='http://apis.juhe.cn/idcard/index?key='+key+'&cardno='+identifice;
    try:
        idinfo=crawl_timeout(url,10,3);
        idstr=json.JSONDecoder().decode(idinfo);
        #print idstr
        rs=idstr['result']['area'].encode("utf-8");
    except:
        #print get_tb_info()
        return ""
    #print "zzzz",rs
    return rs

def get_geo_info(ip):

    url = "http://e.apix.cn/apixlab/ipinfo/ipinfo"
    querystring = {"ip":ip}
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'apix-key': "a8bbd3a565b04acf600e6b053beffea2"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response.text)
    


class PhoneInfo():
    def __init__(self):
        self.province = ""
        self.city = ""
        self.supplier = ""
class EXT_API():

    """Docstring for . """

    def __init__(self):
        """TODO: to be defined1. """
        self.tel_map = {}
        self.phone_map= {}
        self.sms_badword_map= {}
        self.sense_badword_list =[]
        tel_file = settings.TEL_NUM_FILE
        self.init_tel_map(tel_file)
        self.init_phone_map(phone_file)
        self.init_sms_badword()
        self.init_sense_badword()
    
    def init_sense_badword(self):

        f = settings.SENSE_BAD_WORD_FILE
        for line in open(f,'r'):
            if line[0:1]=='#':
                continue
            try:
                ##print 'xxx',line
                if len(line)>0:
                    line = line.encode("utf-8")
                    wl  = line.strip().split(',')
                    self.sense_badword_list.append(wl)
            except:
                base_logger.error(get_tb_info())
                #print get_tb_info()
                continue
               
    def have_sense_badword(self,string):

        s = string.encode("utf-8")
        for w in self.sense_badword_list:
        
            have = True
            for ww in w:
                ##print 'haah',ww,s
                if ww not in s :
                    have =  False
                    break
            if have ==True:
                return True
        return False            

    def init_sms_badword(self):
        f = settings.SMS_BAD_WORD_FILE
        for line in open(f,'r'):
            try:
                word  = line.strip().split('\t')[0]
                self.sms_badword_map[word]=1 
            except:
                continue
        
        return 
    def sms_have_bad_word(self,string):

        for k,v in self.sms_badword_map.items():
            if k in string:
                return True
        return False

    def init_phone_map(self,file):
        pmap = {}

        for line in open(file,'r'):
            flist = line.strip().split(',')
            if len(flist) <5:
                continue
            pi = PhoneInfo()

            p = flist[1].replace("\"",'')
            pc = flist[2].replace("\"",'')
            clist = pc.split(' ')
            if len(clist) ==2:
                pi.province = clist[0]
                pi.city = clist[1]
            else:
                pi.province = clist[0]
                pi.city = pi.province
            pi.supplier = flist[3]

            pmap[p]= pi

        self.phone_map = pmap
        return True


    def init_tel_map(self,file):

        p = ""
        tel_map = {}
        for line in open(file,'r'):
            flist = line.strip().split(' ')
            if len(flist) ==1:
                p = flist[0]
            elif len(flist) ==2:
                p = flist[0]
                t = flist[1]
                tel_map[t] = p +'-'+p
            else:
                index = 0
                c = ""
                for f in flist:
                    if index == 0:
                        c = f
                    else:
                        tel_map[f] = p +'-'+c
                    index +=1
                    index = index % 2
        self.tel_map = tel_map
    def get_info_by_id(self,id_str):

        #file = settings.ID_FILE
        info = judge(id_str)
        #location = info['province'] +info['city'] +info['discrict']
        location = info
        sex = ""
        birthday = ""
        if len(id_str) ==15:
            birthday = "19"+id_str[6:6+6]
            if int (id_str[-1]) %2 ==0:
                sex = '女'
            else:
                sex = '男'
        else:
            birthday = id_str[6:6+8]
            if int (id_str[-2]) %2 ==0:
                sex = '女'
            else:
                sex = '男'
        return sex,location,birthday

    #查询通讯录归属地
    def get_phone_location(self,num):
        g ={}
        g['province'] = "none"
        g['city'] = "none"
        g['supplier'] = "none"
        if len(num) ==11 and num[0]=='1':
            #手机号
            pp = num[0:7]
            if pp in self.phone_map:
                pi = self.phone_map[pp]
                g['province'] = pi.province
                g['city'] = pi.city
                g['supplier'] = pi.supplier.replace("\"",'')

        else:
            #固话
            n1 = num[0:3]
            n2 = num[0:4]
            if n1 in self.tel_map:
                ff = self.tel_map[n1].split('-')
                g['province'] = ff[0]
                g['city'] = ff[1]
            elif n2 in self.tel_map:
                ff = self.tel_map[n2].split('-')
                g['province'] = ff[0]
                g['city'] = ff[1]

        return g

    def get_gps_location_new(self,latitude,longitude):


        gps = {}
        gps ['formatted_address']=''

        url = "http://api.map.baidu.com/geocoder?location=%s,%s&output=xml"
        turl = url %(latitude,longitude)
        page = crawl_timeout(turl,20,3)
        if page== None:
            #print "gps api get error"
            base_logger.error("gps api get error")
            return gps
        else:
            s = page
            gps['formatted_address'] = s.split("<formatted_address>")[1].split("</formatted_address>")[0]
            gps['city'] = s.split("<city>")[1].split("</city>")[0]
            gps['province'] = s.split("<province>")[1].split("</province>")[0]
            gps['streetNumber'] = s.split("<streetNumber>")[1].split("</streetNumber>")[0]
            gps['street'] = s.split("<street>")[1].split("</street>")[0]
            gps['district'] = s.split("<district>")[1].split("</district>")[0]

            return gps


    def get_ip_location(self,ip):
        g = {}

        res = get_geo_info(ip)
        if len(res)>=3:
            g['country'] = res[0]
            g['province'] = res[1]
            g['city'] = res[2]
            return g
        else:
            return None
    #判断电话号码
    def is_normal_phonenum(self,phonenum):
        normal_phone_flag=[3,5,7,8]
        if len(phonenum)==0 or len(phonenum)>12:
            return False
        else:
            #正常手机号
            if len(phonenum)==11 and phonenum[0]=='1' and phonenum[1] in ['3','4','5','7','8']:
                return True
            #(区号+号码)
            reg_list=self.tel_map.keys()
            phonenum_prefix_4=phonenum[:4] in reg_list and (len(phonenum)==11 or len(phonenum)==12)
            phonenum_prefix_3=phonenum[:3] in reg_list and (len(phonenum)==10 or len(phonenum)==11)
            if phonenum_prefix_4 or phonenum_prefix_3:
                return True
        return False

if __name__ == '__main__':
    api = EXT_API()
    #print api.get_info_by_id("110222198104116018")

