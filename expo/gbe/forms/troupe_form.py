from django.forms import (
    ModelForm,
    ModelMultipleChoiceField,
)
from gbe.models import Troupe
from gbe_forms_text import (
    persona_help_texts,
    persona_labels,
)
from gbe.forms.common_queries import visible_personas


class TroupeForm (ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    membership = ModelMultipleChoiceField(
        queryset=visible_personas)

    class Meta:
        model = Troupe
        fields = '__all__'
        help_texts = persona_help_texts
        labels = persona_labels
