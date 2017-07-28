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
from filer.models.imagemodels import Image
from filer.models.foldermodels import Folder
from django.contrib.auth.models import User


class PersonaForm (ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    upload_img = ImageField(
        help_text=persona_help_texts['promo_image'],
        label=persona_labels['promo_image'],
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.fields['upload_img'] = ImageField(
                help_text=persona_help_texts['promo_image'],
                label=persona_labels['promo_image'],
                initial=kwargs.get('instance').img,
                required=False,
            )

    def save(self, commit=True):
        performer = super(ModelForm, self).save(commit=False)
        if commit and self['upload_img'] and (
                self['upload_img'].value() != performer.img):
            if self['upload_img'].value():
                superuser = User.objects.get(username='admin_img')
                folder, created = Folder.objects.get_or_create(
                    name='Performers')
                img, created = Image.objects.get_or_create(
                    owner=superuser,
                    original_filename=self['upload_img'].value().name,
                    file=self['upload_img'].value(),
                    folder=folder,
                    author="%s" % str(performer.name,),
                )
                img.save()
                performer.img_id = img.pk
            else:
                performer.img = None
        performer.save()

        return performer

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
