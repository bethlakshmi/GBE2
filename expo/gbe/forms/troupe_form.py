from django.forms import (
    ModelForm,
)
from gbe.models import Troupe
from gbe_forms_text import (
    persona_help_texts,
    persona_labels,
)


class TroupeForm (ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = Troupe
        fields = '__all__'
        help_texts = persona_help_texts
        labels = persona_labels
