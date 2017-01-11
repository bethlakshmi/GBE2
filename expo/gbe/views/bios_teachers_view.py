from django.shortcuts import render
from django.core.urlresolvers import reverse
from expo.gbe_logging import log_func

from scheduler.functions import (
    get_scheduled_events_by_role,
)
from gbe.models import Performer
from gbe.functions import (
    get_current_conference,
    get_conference_by_slug,
    conference_list,
)


@log_func
def BiosTeachersView(request):
    '''
    Display the teachers bios.  Teachers are anyone teaching,
    moderating or being a panelist.
    '''
    conf_slug = request.GET.get('conference', None)
    if not conf_slug:
        conference = get_current_conference()
    else:
        conference = get_conference_by_slug(conf_slug)
    conferences = conference_list()
    performers = Performer.objects.all()
    bios = []
    workers, commits = get_scheduled_events_by_role(
        conference,
        ["Teacher", "Moderator", "Panelist"])

    for performer in performers:
        classes = []
        for worker in workers.filter(_item=performer):
            for commit in commits.filter(resource=worker):
                classes += [{'role': worker.role, 'event': commit.event}]
        if len(classes) > 0:
            bios += [{'bio': performer, 'classes': classes}]

    template = 'gbe/bio_list.tmpl'
    context = {'bios': bios,
               'bio_url': reverse('bios_teacher',
                                  urlconf='gbe.urls'),
               'title': 'Conference Bios',
               'conferences': conferences}

    return render(request, template, context)
