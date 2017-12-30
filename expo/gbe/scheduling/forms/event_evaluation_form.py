from django.forms import (
    BooleanField,
    CharField,
    ChoiceField,
    Form,
    RadioSelect,
    Textarea,
)
from gbe.models import Class
from gbetext import grade_options


class HorizontalRadioSelect(RadioSelect):

    def __init__(self, *args, **kwargs):
        super(HorizontalRadioSelect, self).__init__(*args, **kwargs)

        self.renderer.inner_html = '<td>{choice_value}{sub_widgets}</td>'


class EventEvaluationForm(Form):
    '''
    Form for selecting the type of event to create
    '''
    required_css_class = 'required'
    error_css_class = 'error'


    def __init__(self, *args, **kwargs):
        questions = None
        if 'questions' in kwargs:
            questions = kwargs.pop('questions')
        super(EventEvaluationForm, self).__init__(*args, **kwargs)
        for question in questions:
            if question.answer_type == "text":
                self.fields['question%d' % question.pk] = CharField(
                    label=question.question,
                    help_text=question.help_text,
                    widget=Textarea
                )
            if question.answer_type == "grade":
                self.fields['question%d' % question.pk] = ChoiceField(
                    label=question.question,
                    help_text=question.help_text,
                    choices=grade_options,
                    widget=HorizontalRadioSelect(),
                )
            if question.answer_type == "boolean":
                self.fields['question%d' % question.pk] = BooleanField(
                    label=question.question,
                    help_text=question.help_text,
                )