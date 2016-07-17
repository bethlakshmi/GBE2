from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag('scheduler/tag_templates/volunteer_schedule.tmpl')
def volunteer_schedule(user):
    pass
