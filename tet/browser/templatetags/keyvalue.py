from django import template

register = template.Library()

@register.simple_tag
def keyvalue(dict, key):
    return dict[key]
