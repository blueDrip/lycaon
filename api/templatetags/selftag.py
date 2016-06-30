# encoding: utf-8
from django import template
import  binascii
register = template.Library()

@register.filter(name='cut11')
def cut1(value, arg):
    return value.replace(arg, '_')

@register.filter(name='banary_to_str')
def binary_to_string(value,arg):
    return binascii.b2a_hex(value).upper()