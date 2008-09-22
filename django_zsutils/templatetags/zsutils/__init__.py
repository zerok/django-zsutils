"""
This module contains template tags for instance for a unified pagination
look and feel.
"""
from django.conf import settings
from django.utils.dateformat import format
from django import template

register = template.Library()

@register.filter('datetime')
def datetime(value):
    return format(value, settings.DATETIME_FORMAT)

