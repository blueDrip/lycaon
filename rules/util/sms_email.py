#!/usr/bin/env python
# encoding: utf-8
import os

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class MyEmail:
    def __init__(self,content):
        self.user = None
        self.passwd = None
        self.content= content
        self.to_list = []
        self.cc_list = []
        self.tag = None
        self.doc = None

        self.doc_list = []

    #发送邮件
    def send(self):
        #try:
        server = smtplib.SMTP_SSL("smtp.qq.com",port=465)
        server.login(self.user,self.passwd)
        print "login successful!"
        if self.doc_list:
            server.sendmail("<%s>"%self.user, self.to_list, self.get_attach())
        else:
            msg = MIMEText(self.content,_subtype='plain',_charset='gb2312')
            msg['Subject'] =self.tag 
            msg['From']=self.user
            msg['To'] = ";".join(self.to_list) 
            server.sendmail("<%s>"%self.user, self.to_list, msg.as_string())
        server.close()
        print "send email successful"
        #except Exception,e:
        #   print "send email failed %s"%e4
    def get_attach(self):
        attach = MIMEMultipart()
        if self.tag:
        #主题,最上面的一行
            attach["Subject"] = self.tag
        if self.user:
        #显示在发件人
            attach["From"] = "发件人姓名，可以自定义<%s>"%self.user
        if self.to_list:
        #收件人列表
            attach["To"] = ";".join(self.to_list)
        if self.cc_list:
        #抄送列表
            attach["Cc"] = ";".join(self.cc_list)
        if self.doc:
            #估计任何文件都可以用base64，比如rar等
            #文件名汉字用gbk编码代替
            name = os.path.basename(self.doc).encode("utf-8")
            f = open(self.doc,"rb")
            doc = MIMEText(f.read(), "base64", "utf-8")
            doc["Content-Type"] = 'application/octet-stream'
            doc["Content-Disposition"] = 'attachment; filename="'+name+'"'
            attach.attach(doc)
            f.close()
            return attach.as_string()
        if self.doc_list:
            for i in self.doc_list:
                name = os.path.basename(i).encode("utf-8")
                f = open(i,"rb")
                doc = MIMEText(f.read(), "base64", "utf-8")
                doc["Content-Type"] = 'application/octet-stream'
                doc["Content-Disposition"] = 'attachment; filename="'+name+'"'
                attach.attach(doc)
                f.close()
            return attach.as_string()
if __name__ =='__main__':
    print 'test'
    my = MyEmail(u'ttttt')
    my.user = "1049787469@qq.com"
    my.passwd = "abcd1243"
    #my.to_list = ["qiuye@daixiaomi.com"]
    my.to_list = ["1049787469@qq.com"]
    my.cc_list = [""]
    my.tag = "订单流量监控报警"
    #my.doc = "/home/qiuye/%s.xlsx"%fname
    ##my.doc_list = [""]
    my.send()



