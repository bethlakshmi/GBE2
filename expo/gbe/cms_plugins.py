from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext as _
from django.template import loader
from gbe.forms import ContactForm
from cms.models.pluginmodel import CMSPlugin

class ContactFormPlugin(CMSPluginBase):
    model = CMSPlugin
    module = _("GBE Plugins")
    name = _("Drop a Line")  # name of the plugin in the interface
    render_template = loader.get_template('gbe/incl_contact_form.tmpl')

    def render(self, context, instance, placeholder):
        context.update({'contact_form':ContactForm()})
        return context
    
class SubscribeEmailPlugin(CMSPluginBase):
    model = CMSPlugin
    module = _("GBE Plugins")
    name = _("Subscribe to Email")  # name of the plugin in the interface
    render_template = loader.get_template('gbe/email_subscribe.tmpl')

class GoFundMePlugin(CMSPluginBase):
    model = CMSPlugin
    module = _("GBE Plugins")
    name = _("Go Fund Me Widget")  # name of the plugin in the interface
    render_template = loader.get_template('gbe/go_fund_me.tmpl')


plugin_pool.register_plugin(ContactFormPlugin)  # register the plugin
plugin_pool.register_plugin(SubscribeEmailPlugin)  # register the plugin
plugin_pool.register_plugin(GoFundMePlugin)  # register the plugin
