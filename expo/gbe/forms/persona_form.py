from django.forms import (
    HiddenInput,
    ImageField,
    ModelForm,
)
from gbe.models import Persona
from gbe_forms_text import (
    persona_help_texts,
    persona_labels,
)
from gbe.expoformfields import FriendlyURLInput


class PersonaForm (ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    upload_img = ImageField(
        help_text=persona_help_texts['promo_image'],
        label=persona_labels['promo_image'],
    )

    class Meta:
        model = Persona
        fields = ['name',
                  'homepage',
                  'bio',
                  'experience',
                  'awards',
                  'performer_profile',
                  'contact',
                  ]
        help_texts = persona_help_texts
        labels = persona_labels
        widgets = {'performer_profile': HiddenInput(),
                   'contact': HiddenInput(),
                   'homepage': FriendlyURLInput,
                   }
