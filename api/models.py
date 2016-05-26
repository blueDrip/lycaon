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

    class Meta:
        db_table = 'user_infos'


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

