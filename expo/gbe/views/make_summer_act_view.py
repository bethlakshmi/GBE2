from gbe.views import MakeActView
from django.http import Http404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.forms import ModelChoiceField
from gbe.ticketing_idd_interface import (
    performer_act_submittal_link,
    verify_performer_app_paid,
)
from gbe.models import (
    Act,
    AudioInfo,
    LightingInfo,
    Performer,
    StageInfo,
    TechInfo,
)
from gbe.forms import (
    SummerActDraftForm,
    SummerActForm,
)
from gbetext import (
    default_act_submit_msg,
    default_act_draft_msg,
)
from gbe.views.act_display_functions import display_invalid_act
from gbe_forms_text import summer_act_popup_text


class MakeSummerActView(MakeActView):
    view_title = 'Propose an Act for The MiniExpo'
    submit_form = SummerActForm
    draft_form = SummerActDraftForm

    def get_initial(self):
        initial = super(MakeSummerActView, self).get_initial()
        if not self.bid_object:
            initial['conference'] = self.conference
        return initial

    def make_context(self):
        context = super(MakeActView, self).make_context()
        context['popup_text'] = summer_act_popup_text
        return context
