# coding=utf8

from django.db import models
# Create your models here.
import datetime
import traceback
from mongoengine import (
    StringField, IntField, Document, DateTimeField, BooleanField,
    ObjectIdField,ListField,DictField,ReferenceField,FloatField,NotUniqueError,
    EmbeddedDocument,
)

from django.db import models
from django.conf import settings
from rules.raw_data import minRule

class RulesInfo(Document):
    valid_name_info = DictField()
    online_shop_info = DictField()
    contact_info = DictField()
    sp_info = DictField()
    credit_info = DictField()
    created_at = DateTimeField()
    user_id = StringField()
