from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag('gbe/tag_templates/mailchimp.tmpl')
def mailchimp():
    if settings.MC_API_KEY == 'TEST':
        return {'have_mc': False}
    return {'mc_api_url': settings.MC_API_URL, 
            'mc_api_user': settings.MC_API_USER,
            'mc_api_id': settings.MC_API_ID,
            'have_mc': True,
            }
