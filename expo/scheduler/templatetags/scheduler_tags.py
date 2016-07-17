from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag('scheduler/tag_templates/volunteer_schedule.tmpl')
def volunteer_schedule(profile):
    events = profile.volunteer_schedule()
    schedule = [
        {'event': str(event),
         'time': "%s - %s" % (event.starttime.strftime("%a, %I:%M %p"),
                              (event.starttime + event.duration).strftime(
                                  "%a, %I:%M %p")),
         'location': str(event.location)}
        for event in events]
    return {'schedule': schedule}
