from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from cms.menu_bases import CMSAttachMenu
from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool


class BidsMenu(CMSAttachMenu):
    name = _("I Want To")  # give the menu a name this is required.

    def get_nodes(self, request):
        """
        This method is used to build the menu tree.
        """
        nodes = []
 
        node1 = NavigationNode(
            "Perform at the Expo",
            reverse('gbe:act_create'),
            1
            )
        node2 = NavigationNode(
            "Teach a Class",
            reverse('gbe:class_create'),
            2
            )
        nodes.append(node1)
        nodes.append(node2)
        return nodes

menu_pool.register_menu(BidsMenu) # register the menu.