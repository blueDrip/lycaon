# encoding: utf-8
from django import template
register = template.Library()

@register.filter(name='cut11')
def cut1(value, arg):
    return value.replace(arg, '-----')

