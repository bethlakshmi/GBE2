from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _
from gbe.menu import BidsMenu

class GBEApphook(CMSApp):
    name = _("GBE")
    urls = ["gbe.urls"]
    menus = [BidsMenu]
    
apphook_pool.register(GBEApphook)
