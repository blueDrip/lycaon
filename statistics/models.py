# coding=utf8

from django.db import models
# Create your models here.
import datetime
import traceback
from mongoengine import (
    StringField, IntField, Document, DateTimeField, BooleanField,
    ObjectIdField,ListField,ListField,ReferenceField,FloatField,NotUniqueError,
    EmbeddedDocument,
)

from django.db import models
from django.conf import settings
from rules.raw_data import minRule

class RulusDetailInfo(Document):
    valid_name_info = ObjectIdField()
    online_shop_info = ObjectIdField()
    contact_info = ObjectIdField()
    sp_info = ObjectIdField()
    credit_info = ObjectIdField()
    user_id = StringField()
