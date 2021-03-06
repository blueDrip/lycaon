from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
#class Question(models.Model):
#    question_text = models.CharField(max_length=200)
#    pub_date = models.DateTimeField('date published')

#    class Meta:
#        db_table='rules_question'


class Busers(models.Model):
    user_id = models.BinaryField(db_column='id',primary_key=True)
    password_digest = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    token = models.CharField(max_length=255)
    reg_location = models.CharField(max_length=255)
    last_login_time = models.DateTimeField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'users'

class Profile(models.Model):
    pid = models.IntegerField(db_column='id',primary_key=True)
    user_id = models.BinaryField()
    is_certification = models.IntegerField(default = 0)
    phone_place = models.CharField(max_length = 255)
    phone_type = models.CharField(max_length = 255)
    trust_score = models.FloatField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    education = models.CharField(max_length= 255)
    marry_info = models.CharField(max_length = 255)
    profession = models.CharField(max_length = 255)
    passwd = models.CharField(max_length = 255)
    user = models.ForeignKey(Busers)
    class Meta:
        db_table = 'user_infos'

class ucredit(models.Model):
    uc_id = models.IntegerField(db_column='id',primary_key=True)
    user_id = models.BinaryField()

    is_idcard_auth = models.IntegerField(default = 1)
    idcard_auth_token = models.CharField(max_length=255,default = '1111')

    is_isp_auth = models.IntegerField()
    isp_token = models.CharField(max_length=255)
    
    is_taobao_auth = models.IntegerField()
    is_taobao_auth = models.CharField(max_length=255)

    is_jingdong_auth = models.IntegerField()
    jingdong_token = models.CharField(max_length=255)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    is_contact = models.IntegerField()
    contact_token = models.CharField(max_length=255)
    is_send = models.IntegerField()  
  
    class Meta:
        db_table = 'user_credits'

'''order info'''
'''
class Loan(models.Model):
    loan_id = models.IntegerField(db_column='id',primary_key=True)
    user_id = models.BinaryField()
    amount = models.FloatField()
    state = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    class Meta:
        db_table = 'loans'

class LoanOrder(models.Model):
    order_id = models.IntegerField(db_column='id',primary_key=True)
    loan = models.OneToOneField(Loan)
    amount = models.FloatField()
    pay_end_time = models.DateTimeField()
    audit_time = models.DateTimeField()
    audit_status = models.IntegerField()
    stage = models.IntegerField()
    loan_fee = models.FloatField()
    pay_status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    service_free = models.FloatField()
    purpose = models.CharField(max_length=255)

    class Meta:
        db_table = 'loan_orders'
'''

class Idcardauthlogdata(models.Model):
    id = models.AutoField(primary_key=True)

    # apixkey = models.CharField(max_length=255L, db_column='ApixKey', blank=True) # Field name made lowercase.
    uuid = models.CharField(max_length=255L, db_column='Uuid', blank=True) # Field name made lowercase.
    name = models.CharField(max_length=255L, db_column='Name', blank=True) # Field name made lowercase.
    cardno = models.CharField(max_length=255L, db_column='Cardno', blank=True) # Field name made lowercase.
    code = models.IntegerField(null=True, db_column='Code', blank=True) # Field name made lowercase.
    msg = models.CharField(max_length=255L, db_column='Msg', blank=True) # Field name made lowercase.
    createtime = models.CharField(max_length=255L, db_column='CreateTime', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'idcardauth_logdata'

class Yunyinglogdata(models.Model):
    id = models.AutoField(primary_key=True)
    typed = models.CharField(max_length=255L, db_column='Typed', blank=True) # Field name made lowercase.

    # apixkey = models.CharField(max_length=255L, db_column='ApixKey', blank=True) # Field name made lowercase.
    uuid = models.CharField(max_length=255L, db_column='Uuid', blank=True) # Field name made lowercase.
    phoneno = models.CharField(max_length=255L, db_column='Phoneno', blank=True) # Field name made lowercase.
    passwd = models.CharField(max_length=255L, db_column='Passwd', blank=True) # Field name made lowercase.
    createtime = models.CharField(max_length=255L, db_column='CreateTime', blank=True) # Field name made lowercase.
    class Meta:
        db_table = 'yunying_logdata'

class Dianshanglogdata(models.Model):
    id = models.AutoField(primary_key=True)
    typed = models.CharField(max_length=255L, db_column='Typed', blank=True) # Field name made lowercase.

    # apixkey = models.CharField(max_length=255L, db_column='ApixKey', blank=True) # Field name made lowercase.
    uuid = models.CharField(max_length=255L, db_column='Uuid', blank=True) # Field name made lowercase.
    loginname = models.CharField(max_length=255L, db_column='LoginName', blank=True) # Field name made lowercase.
    passwd = models.CharField(max_length=255L, db_column='Passwd', blank=True) # Field name made lowercase.
    createtime = models.CharField(max_length=255L, db_column='CreateTime', blank=True) # Field name made lowercase.
    login_ret = models.IntegerField(null=True, db_column='Login_ret',default=0L) # Field name made lowercase.
    mutal_ret = models.CharField(max_length=255L, db_column='Mutal_ret',null=True) # Field name made lowercase.

    class Meta:
        db_table = 'dianshang_logdata'

class BankAccount(models.Model):
    account_type = models.CharField(max_length=8)
    token = models.CharField(max_length=32,primary_key=True)
    login_name = models.CharField(max_length=32)
    created_at = models.DateTimeField()
     
    class Meta:
        db_table = 'bank_account'
class adminAccount(models.Model):
    id = models.AutoField(primary_key=True)
    login_name = models.CharField(max_length=255,blank=False)
    pwd = models.CharField(max_length=255,blank=False)
    login_time = models.DateTimeField()
    
    class Meta:
        db_table = 'users'
class privaliage(models.Model):
    privaliage_id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=255,blank=False,unique=True)
    privaliage_name = models.CharField(max_length=255,blank=False)
   
    class Meta:
        db_table = 'privaliage'

class role(models.Model):
    rid = models.AutoField(primary_key=True)
    descname = models.CharField(max_length=255,blank=False,unique=True)
    privilage_id = models.IntegerField(blank=False,default=1)
    class Meta:
        db_table = 'role'
class privaliage_role (models.Model):
    id = models.AutoField(primary_key=True)
    role_id = models.IntegerField(blank=False)
    privaliage_id = models.IntegerField(blank=False)

    class Meta:
        db_table = 'privilage_role'
class user_role(models.Model):
    urid = models.AutoField(primary_key=True)
    uid = models.IntegerField(blank=False)
    rid = models.IntegerField(blank=False)
 
    class Meta:
        db_table = 'user_role'
