from django.shortcuts import (
    render,
    get_object_or_404,
)
from django.http import HttpResponseRedirect
from scheduler.models import *
from scheduler.forms import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.urlresolvers import reverse
from scheduler.views.functions import (
    get_events_display_info,
)
from gbe.functions import (
    get_current_conference,
    validate_perms,
)


@login_required
@never_cache
def event_list(request, event_type=''):
    '''
    List of events (all, or by type)
    '''
    profile = validate_perms(request, ('Scheduling Mavens',))
    if request.method == 'POST':
        event_type = request.POST['event_type']

    if event_type.strip() == '':
        template = 'scheduler/select_event_type.tmpl'
        event_type_options = list(
            set([ei.__class__.__name__
                 for ei in EventItem.objects.filter(
                         visible=True).select_subclasses()]))
        return render(request,
                      template,
                      {'type_options': event_type_options})

    header = ['Title',
              'Location',
              'Date/Time',
              'Duration',
              'Type',
              'Max Volunteer',
              'Current Volunteer',
              'Detail',
              'Edit Schedule',
              'Delete']
    events = get_events_display_info(event_type)

    template = 'scheduler/events_review_list.tmpl'
    create_url = reverse('create_event',
                         urlconf='gbe.scheduling.urls',
                         args=[event_type])
    if event_type == "Class":
        create_url = reverse('create_class_wizard',
                             urlconf='gbe.scheduling.urls',
                             args=[get_current_conference().conference_slug])
    elif event_type == "Show":
        create_url = reverse('create_ticketed_event_wizard',
                             urlconf='gbe.scheduling.urls',
                             args=[get_current_conference().conference_slug,
                                   "show"])
    return render(request,
                  template,
                  {'events': events,
                   'header': header,
                   'create_url': create_url})


@login_required
@never_cache
def schedule_acts(request, show_id=None):
    '''
    Display a list of acts available for scheduling, allows setting show/order
    '''
    validate_perms(request, ('Scheduling Mavens',))

    import gbe.models as conf

    # came from the schedule selector
    if request.method == "POST":
        show_id = request.POST.get('show_id', 'POST')

    # no show selected yet
    if show_id is None or show_id.strip() == '':
        template = 'scheduler/select_event_type.tmpl'
        show_options = EventItem.objects.all().select_subclasses()
        show_options = filter(
            lambda event: (
                type(event) == conf.Show) and (
                event.get_conference().status != 'completed'), show_options)
        return render(request, template, {'show_options': show_options})

    # came from an ActSchedulerForm
    if show_id == 'POST':
        alloc_prefixes = set([key.split('-')[0] for key in request.POST.keys()
                              if key.startswith('allocation_')])
        for prefix in alloc_prefixes:
            form = ActScheduleForm(request.POST, prefix=prefix)
            if form.is_valid():
                data = form.cleaned_data
            else:
                continue  # error, should log
            alloc = get_object_or_404(ResourceAllocation,
                                      id=prefix.split('_')[1])
            alloc.event = data['show']
            alloc.save()
            try:
                ordering = alloc.ordering
                ordering.order = data['order']
            except:
                ordering = Ordering(allocation=alloc, order=data['order'])
            ordering.save()

        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

    # get allocations involving the show we want
    show = get_object_or_404(conf.Show, pk=show_id)
    event = show.scheduler_events.first()

    allocations = ResourceAllocation.objects.filter(event=event)
    allocations = [a for a in allocations if type(a.resource.item) == ActItem]

    forms = []
    for alloc in allocations:
        actitem = alloc.resource.item
        act = actitem.act
        if act.accepted != 3:
            continue
        details = {}
        details['title'] = act.b_title
        details['performer'] = act.performer
        details['show'] = event
        try:
            details['order'] = alloc.ordering.order
        except:
            o = Ordering(allocation=alloc, order=0)
            o.save()
            details['order'] = 0

        forms.append([details, alloc])
    forms = sorted(forms, key=lambda f: f[0]['order'])
    new_forms = []
    for details, alloc in forms:
        new_forms.append((
            ActScheduleForm(initial=details,
                            prefix='allocation_%d' % alloc.id),
            details['performer'].contact.user_object.is_active))

    template = 'scheduler/act_schedule.tmpl'
    return render(request,
                  template,
                  {'forms': new_forms})
