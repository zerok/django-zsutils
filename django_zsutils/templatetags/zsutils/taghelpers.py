"""
:Requirements: django-tagging

This module contains some additional helper tags for the django-tagging
project. Note that the functionality here might already be present in
django-tagging but perhaps with some slightly different behaviour or 
usage.
"""

from django import template
from django.core.urlresolvers import reverse as url_reverse
from tagging.utils import parse_tag_input

register = template.Library()

class TagsForObjectNode(template.Node):
    def __init__(self, tags_string, urlname, junctor=None, last_junctor=None):
        self.tags_string = template.Variable(tags_string)
        self.junctor = junctor is None and ', ' or junctor.lstrip('"').rstrip('"')
        self.last_junctor = last_junctor is None and ' and ' or last_junctor.lstrip('"').rstrip('"')
        self.urlname = urlname

    def render(self, context):
        tags = parse_tag_input(self.tags_string.resolve(context))
        tags = ['<a href="%s" rel="tag">%s</a>' % (url_reverse(self.urlname, kwargs={'tag':t}), t) for t in tags]
        if len(tags) > 2:
            first_part = self.junctor.join(tags[:-1])
            return first_part + self.last_junctor + tags[-1]
        if len(tags) == 2:
            return self.last_junctor.join(tags)
        return self.junctor.join(tags)

@register.tag('object_tags')
def tags_for_object(parser, token):
    """
    Simple tag for rendering tags of an object

    Usage::
        
        {% object_tags object.tags blog-tag ", " " and " %}
    
    The last two arguments determine the junctor between the tag names with
    the last being the last junctor being used.
    """
    variables = token.split_contents()[1:]
    return TagsForObjectNode(*variables)
