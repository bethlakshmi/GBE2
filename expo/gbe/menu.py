from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from cms.menu_bases import CMSAttachMenu
from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool

from gbe.functions import *
from gbe.models import *

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
    
class LoginMenu(Menu):
    name = _("Your Account")  # give the menu a name this is required.

    def get_nodes(self, request):
        """
        menus for all users or potential users to do account management
        """
        nodes = []
 
        nodes.append(NavigationNode(_("Your Account"), "", 1,
                                    attr={'visible_for_anonymous': False} ))
        nodes.append(NavigationNode(_("Update Profile"), reverse('gbe:profile_update'), 2, 1,
                                    attr={'visible_for_anonymous': False}))
        nodes.append(NavigationNode(_("Logout"), reverse('gbe:logout'), 3, 1,
                                    attr={'visible_for_anonymous': False}))
        nodes.append(NavigationNode(_("Join Today"), "", 4,
                                    attr={'visible_for_authenticated': False} ))
        nodes.append(NavigationNode(_("Register"), reverse('gbe:register'), 5, 4,
                                    attr={'visible_for_authenticated': False}))
        nodes.append(NavigationNode(_("Login"), reverse('gbe:login'), 6, 4,
                                    attr={'visible_for_authenticated': False} ))

        return nodes

class SpecialMenu(Menu):
    name = _("Special")
    
    def get_nodes(self, request):
        """
        populate for users based on profile.  Users must have special privileges to use this
        """
        nodes = []
        user = request.user
        
        if user.is_authenticated() and validate_profile(request) and user.profile.special_privs:
            nodes.append(NavigationNode(_("Special"), "", 1 ))
            nodes.append(NavigationNode(_("Reporting"), reverse('reporting:report_list'), 2, 1 ))
            for priv in user.profile.special_privs:
                n=3
                
                if priv["url"] and len(priv["url"]) > 0:
                    nodes.append(NavigationNode(priv["title"], priv["url"], n, 1))
                    n = n+1
                    
        return nodes
        
        
        
menu_pool.register_menu(BidsMenu) # register the menu.
menu_pool.register_menu(SpecialMenu) # register the menu.
menu_pool.register_menu(LoginMenu) # register the menu.