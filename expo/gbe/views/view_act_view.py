from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from expo.gbe_logging import log_func
from gbe.forms import (
    ActEditForm,
    PersonaForm,
    TroupeForm,
)
from gbe.models import (
    Act,
    Troupe,
)
from gbe.functions import validate_perms


@login_required
@log_func
def ViewActView(request, act_id):
    '''
    Show a bid as a read-only form.
    '''
    act = get_object_or_404(Act, id=act_id)
    if act.performer.contact != request.user.profile:
        validate_perms(request, ('Act Reviewers',), require=True)
    audio_info = act.tech.audio
    stage_info = act.tech.stage
    actform = ActEditForm(
        instance=act,
        prefix='The Act',
        initial={'track_title': audio_info.track_title,
                 'track_artist': audio_info.track_artist,
                 'track_duration': audio_info.track_duration,
                 'act_duration': stage_info.act_duration}
    )

    if Troupe.objects.filter(pk=act.performer.pk).exists():
        instance = Troupe.objects.get(pk=act.performer.pk)
        performer = TroupeForm(instance=instance,
                               prefix='The Troupe')
    else:
        performer = PersonaForm(instance=act.performer,
                                prefix='The Performer(s)')

    return render(request, 'gbe/bid_view.tmpl',
                  {'readonlyform': [actform, performer]})
