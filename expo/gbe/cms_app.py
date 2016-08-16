from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


# this is largely a proof of concept right now,
class GBEApphook(CMSApp):
    name = _("GBE")
    urls = ["gbe.urls"]

apphook_pool.register(GBEApphook)
