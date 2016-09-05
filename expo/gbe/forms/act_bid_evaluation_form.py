from django.forms import (
    ModelForm,
    HiddenInput,
)
from gbe.models import ActBidEvaluation
from gbe.forms import (
    ShowVoteField,
    ShowVoteWidget,
    )

class ActBidEvaluationForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    primary_vote = ShowVoteField()
    secondary_vote = ShowVoteField()


    class Meta:
        model = ActBidEvaluation
        fields = '__all__'
        widgets = {'evaluator': HiddenInput(),
                   'bid': HiddenInput(),
                   'primary_vote': ShowVoteWidget,
                   'secondary_vote': ShowVoteWidget}
