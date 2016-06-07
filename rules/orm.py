# coding=utf8
from corelib.database import MongoDb
from rules.raw_data import JdData,TaoBao,chinaMobile
from datetime import datetime
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
    
    #jd.save()
    return jd

def tb_orm(cnd={}):
    if not cnd:
        return
    d=MongoDb('101.201.78.139',27017,'app_data','heigeMeixin','app_grant_data')
    c=d.get_collection('taobao').find_one(cnd) or {}
    
    tb=TaoBao()
    tb.taobao_name = 'taobao_name' in c and c['taobao_name'] or ''
    tb.createTime=datetime.now()
    if 'personalInfo' in c:
        if 'huabeiCanUseMoney' in c['personalInfo']:
            tb.huabeiCanUseMoney = c['personalInfo']['huabeiCanUseMoney']
        if 'creditLevel' in c['personalInfo']:
            tb.creditLevel = c['personalInfo']['creditLevel']
        if 'tianMaoAccountName' in c['personalInfo']:
            tb.tianMaoAccountName = c['personalInfo']['tianMaoAccountName']
        if 'taobaoFastRefundMoney' in c['personalInfo']:
            tb.taobaoFastRefundMoney = c['personalInfo']['taobaoFastRefundMoney']
        if 'buyerCreditPoint' in c['personalInfo']:
            tb.buyerCreditPoint = c['personalInfo']['buyerCreditPoint']
        if 'aliPaymFund' in c['personalInfo']:
            tb.aliPaymFund = c['personalInfo']['aliPaymFund']
        if 'tianMaoPoints' in c['personalInfo']:
            tb.tianMaoPoints=c['personalInfo']['tianMaoPoints']
        if 'taobaoLevel' in c['personalInfo']:
            tb.taobaoLevel=c['personalInfo']['taobaoLevel']
        if 'aliPaymFundProfit' in c['personalInfo']:
            tb.aliPaymFundProfit=c['personalInfo']['aliPaymFundProfit'] or '0'
        if 'aliPayRemainingAmount' in c['personalInfo']:
            tb.aliPayRemainingAmount=c['personalInfo']['aliPayRemainingAmount'] or '0'
        if 'huabeiTotalAmount' in c['personalInfo']:
            tb.huabeiTotalAmount=c['personalInfo']['huabeiTotalAmount'] or '0'
        if 'growthValue' in c['personalInfo']:
            tb.growthValue = c['personalInfo']['growthValue'] or '0'
        if 'tianmaoExperience' in c['personalInfo']:
            tb.tianmaoExperience=c['personalInfo']['tianmaoExperience'] or '0'
    if 'accountSafeInfo' in c:
        if 'username' in c['accountSafeInfo']:
            tb.username = c['accountSafeInfo']['username']
        if 'pwdProtectedQuestion' in c['accountSafeInfo']:
            tb.pwdProtectedQuestion = c['accountSafeInfo']['pwdProtectedQuestion']

        if 'bindMobile' in c['accountSafeInfo']:
            tb.bindMobile = c['accountSafeInfo']['bindMobile']
        if 'loginPasswdVerify' in c['accountSafeInfo']:
            tb.loginPasswdVerify = c['accountSafeInfo']['loginPasswdVerify']
        if 'identityVerified' in c['accountSafeInfo']:
            tb.identityVerified = c['accountSafeInfo']['identityVerified']
        if 'loginEmail' in c['accountSafeInfo']:
            tb.loginEmail = c['accountSafeInfo']['loginEmail']
        if 'mobileVerified' in c['accountSafeInfo']:
            tb.mobileVerified = c['accountSafeInfo']['mobileVerified']
        if 'safeLevel' in c['accountSafeInfo']:
            tb.safeLevel = c['accountSafeInfo']['safeLevel']
    if 'addrs' in c:
        tb.addrs = c['addrs']
    if 'orderList' in c:
        tb.orderList = c['orderList']
    #tb.save()
    return tb


def china_mobile_orm(cnd={}):
    if not cnd:
        return
    d=MongoDb('101.201.78.139',27017,'app_data','heigeMeixin','app_grant_data')
    c=d.get_collection('yidong').find_one(cnd) or {}

    cmb=chinaMobile()
    if c:
        cmb.currRemainingAmount= c['currRemainingAmount']
        cmb.phonedetail = c['phonedetail']
        cmb.personalInfo = c['personalInfo']
        cmb.openBusiness = c['openBusiness']
        cmb.currPoint = c['currPoint']
        cmb.smsdetail = c['smsdetail']
        cmb.phone_no = c['phone_no']
        cmb.businessOrder = c['businessOrder']
        cmb.netdetail = c['netdetail']
        cmb.fixed = c['fixed']
        cmb.createTime = c['createTime']
        cmb.recharge = c['recharge']
        return cmb
    return None






def phonebook_orm(cnd={}):
    if not cnd:
        return
    d=MongoDb('101.201.78.139',27017,'app_data','heigeMeixin','app_grant_data')
    c=d.get_collection('phonebook').find_one(cnd) or {}











