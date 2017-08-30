from django.forms import (
    ChoiceField,
    HiddenInput,
    ModelForm,
)
from gbe.models import FlexibleEvaluation


class FlexibleEvaluationForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        super(FlexibleEvaluationForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            initial = kwargs.pop('initial')
            self.fields['ranking'] = ChoiceField(
                label=initial['category'].category,
                help_text=initial['category'].help_text,
                required=False)

    class Meta:
        model = FlexibleEvaluation
        fields = ['ranking',
                  'category',
                  'evaluator',
                  'bid']
        widgets = {'category': HiddenInput(),
                   'evaluator': HiddenInput(),
                   'bid': HiddenInput(), }

