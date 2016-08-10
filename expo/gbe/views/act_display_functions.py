from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render
from gbe.models import (
    Act,
    UserMessage,
)
from gbetext import (
    default_act_title_conflict,
    act_not_unique,
)


def display_invalid_act(request, data, form, conference, profile, view):
    if [act_not_unique] in form.errors.values():
        conflict_msg = UserMessage.objects.get_or_create(
            view=view,
            code="ACT_TITLE_CONFLICT",
            defaults={
                'summary': "Act Title, User, Conference Conflict",
                'description': default_act_title_conflict})
        conflict = Act.objects.get(
            conference=conference,
            title=form.data['theact-title'],
            performer__contact=profile)
        if conflict.submitted:
            link = reverse(
                'act_view',
                urlconf='gbe.urls',
                args=[conflict.pk]
            )
        else:
            link = reverse(
                'act_edit',
                urlconf='gbe.urls',
                args=[conflict.pk]
            )
        messages.error(
            request, conflict_msg[0].description % (
                link,
                conflict.title))
    return render(
        request,
        'gbe/bid.tmpl',
        data
    )
