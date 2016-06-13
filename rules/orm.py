# coding=utf8
from corelib.database import MongoDb
from rules.raw_data import JdData,TaoBao,chinaMobile,phonebook,chinaUnicom
from datetime import datetime
def jd_orm(cnd={}):
    if not cnd:
        return
    d=MongoDb('101.201.78.139',27017,'app_data','heigeMeixin','app_grant_data')
    c=d.get_collection('jingdong').find_one(cnd) or {}
    jd=JdData()
    if 'accountSafeInfo' in c:
        jd.safe_priority = 'safeLevel' in c['accountSafeInfo'] and c['accountSafeInfo']['safeLevel'] or ''
    if 'accountLevel' in c:
        jd.growth_value = 'growthValue' in c['accountLevel'] and c['accountLevel']['growthValue'] or ''
        jd.user_level = 'userLevel' in c['accountLevel'] and c['accountLevel']['userLevel'] or ''

    if 'baseInfo' in c:
        jd.sex = 'sex' in c['baseInfo'] and c['baseInfo']['sex'] or ''
        jd.hobbies = 'hobbies' in c['baseInfo'] and c['baseInfo']['hobbies'] or ''
        jd.email_host = 'email' in c['baseInfo'] and c['baseInfo']['email'] or ''
        jd.username = 'username' in c['baseInfo'] and c['baseInfo']['username'] or ''
        jd.real_name = 'realName' in c['baseInfo'] and c['baseInfo']['realName'] or ''
        jd.login_name = 'loginName' in c['baseInfo'] and c['baseInfo']['loginName'] or ''
        jd.nickname = 'nickname' in c['baseInfo'] and c['baseInfo']['nickname'] or ''

    if 'consumeHistroy' in c:
        jd.consume_list= 'record' in c['consumeHistroy'] and c['consumeHistroy']['record'] or []   
    if 'baitiaoInfo' in c:
        if u'未开通' not in c['baitiaoInfo']:  
            jd.baitiao = 'baitiaoInfo' in c and c['baitiaoInfo'] or {}

    jd.small_credit = 'xiaobaixinyong' in c and c['xiaobaixinyong'] or {}
    jd.login_history = 'loginHistory' in c and c['loginHistory'] or ''
    if 'accountSafeInfo' in c:
        detail_list='detail' in c['accountSafeInfo'] and c['accountSafeInfo']['detail'] or []
        for it in detail_list:
            if 'loginNameVerified' in it:
                jd.login_name_varifyied = it
            elif 'emailVerified' in it:
                jd.email_verified = it
            elif 'phoneVerified' in it:
                jd.phone_verifyied = it
            elif 'payPasswdVerified' in it:
                jd.payPasswdVerified = it
            elif 'indentifyVerified' in it:
                jd.indentify_verified = it
            elif 'licenseVerified' in it:
                jd.license_verified = it 
    jd.bankinfo = 'bindBankCards' in c and c['bindBankCards'] or []
    jd.address = 'orderAddress' in c and c['orderAddress'] or ''
    jd.jd_login_name = 'jd_login_name' in c and c['jd_login_name'] or ''
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


def china_unicom_orm(cnd={}):
    if not cnd:
        return None
    d=MongoDb('101.201.78.139',27017,'app_data','heigeMeixin','app_grant_data')
    c=d.get_collection('liantong').find_one(cnd) or {}

    cub=chinaUnicom()
    if c:
        cub.base_info = c['base_info']
        cub.phone_no = c['phone_no']
        cub.yue_jifen = c['yue_jifen'] 
        cub.recharge = c['rechargedetail']
        cub.phonedetail = c['phonedetail']
        cub.smsdetail = c['smsdetail']
        cub.netdetail = c['netdetail']
        cub.others = c['others']
        cub.personalInfo = {}
        cub.createTime = c['createTime']
        return cub    
    return None


def phonebook_orm(cnd={}):
    if not cnd:
        return None
    d=MongoDb('101.201.78.139',27017,'app_data','heigeMeixin','app_grant_data')
    c=d.get_collection('phonebook').find_one(cnd) or {}

    pb = phonebook()
    if c:
        pb.user_id = 'xxx'
        pb.name = c['name']
        pb.phone = c['phone']
        pb.linkmen = c['linkmen']
        pb.device_id = c['device_id']
        return pb
    return None

