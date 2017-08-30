from django.forms import (
    ChoiceField,
    HiddenInput,
    ModelForm,
    RadioSelect,
)
from gbe.models import FlexibleEvaluation


class HorizontalRadioSelect(RadioSelect):

    def __init__(self, *args, **kwargs):
        super(HorizontalRadioSelect, self).__init__(*args, **kwargs)

        self.renderer.inner_html = '<td>{choice_value}{sub_widgets}</td>'


class FlexibleEvaluationForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        super(FlexibleEvaluationForm, self).__init__(*args, **kwargs)
        choice_set = [("", "")]
        choice_set += [(i, "") for i in range(0, 6)]
        if 'initial' in kwargs:
            initial = kwargs.pop('initial')
            self.fields['ranking'] = ChoiceField(
                label=initial['category'].category,
                help_text=initial['category'].help_text,
                required=False,
                widget=HorizontalRadioSelect(),
                choices=choice_set)

    class Meta:
        model = FlexibleEvaluation
        fields = ['ranking',
                  'category',
                  'evaluator',
                  'bid']
        widgets = {'category': HiddenInput(),
                   'evaluator': HiddenInput(),
                   'bid': HiddenInput(), }

