# coding=utf8
from corelib.database import MongoDb
from rules.raw_data import JdData

def jd_orm(cnd={}):
    if not cnd:
        return
    d=MongoDb('101.201.78.139',27017,'app_data','heigeMeixin','app_grant_data')
    c=d.get_collection('jingdong').find_one(cnd) or {}
    jd=JdData()

    jd.safe_priority = 'safe_priority' in c and c['safe_priority'] or ''
    jd.growth_value = 'growth_value' in c and c['growth_value'] or ''
    jd.sex = 'sex' in c and c['sex'] or ''
    jd.vip_change_history = 'vip_change_historym' in c and c['vip_change_history'] or ''
    jd.hobbies = 'hobbies' in c and c['hobbies'] or ''
    jd.three_month_before_consume = 'three_month_before_consume' in c and c['three_month_before_consume'] or ''
    jd.three_month_consume ='three_month_consume' in c and c['three_month_consume'] or ''
    jd.baitiao = 'baitiao' in c and c['baitiao'] or {}
    jd.login_history = 'login_history' in c and c['login_history'] or ''
    jd.phone_verifyied = 'phone_verifyied' in c and c['phone_verifyied'] or ''
    jd.email_host = 'email_host' in c and c['email_host'] or ''
    jd.username = 'username' in c and c['username'] or ''
    jd.bankinfo = 'bankinfo' in c and c['bankinfo'] or ''
    jd.passwd_verifyied = 'passwd_verifyied' in c and c['passwd_verifyied'] or ''
    jd.indentify_verified = 'indentify_verified' in c and c['indentify_verified'] or ''
    jd.address = 'address' in c and c['address'] or ''
    jd.nickname = 'nickname' in c and c['nickname'] or ''
    jd.license = 'license' in c and c['license'] or ''
    jd.jd_login_name = 'jd_login_name' in c and c['jd_login_name'] or ''
    jd.email_verified = 'email_verified' in c and c['email_verified'] or ''
    jd.real_name = 'real_name' in c and c['real_name'] or ''
    jd.user_level = 'user_level' in c and c['user_level'] or ''
    jd.pay_passwd_verified = 'pay_passwd_verified' in c and c['pay_passwd_verified'] or ''
    jd.login_name = 'login_name' in c and c['login_name'] or ''
    
    jd.save()
