from django.forms import (
    ModelForm,
    HiddenInput,
)
from gbe.models import (
    ActBidEvaluation,
    Show
)
from gbe.forms import (
    ShowVoteField,
)
from django.forms.models import ModelChoiceField
from gbe.functions import get_current_conference


class ActBidEvaluationForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    primary_vote = ShowVoteField()
    secondary_vote = ShowVoteField()

    def __init__(self, *args, **kwargs):
        super(ActBidEvaluationForm, self).__init__(*args, **kwargs)
        shows=Show.objects.filter(conference=get_current_conference())
        show_choices = [(show.pk, show) for show in shows]

        self.fields['primary_vote'].widget.widgets[0].choices = show_choices
        self.fields['secondary_vote'].widget.widgets[0].choices = show_choices

    class Meta:
        model = ActBidEvaluation
        fields = '__all__'
        widgets = {'evaluator': HiddenInput(),
                   'bid': HiddenInput(),}
