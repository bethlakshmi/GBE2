from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from cms.menu_bases import CMSAttachMenu
from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool

from gbe.functions import *
from gbe.models import *

'''
  This is the best simulation of our old login menu I could come up with
  - the Django Menu doesn't offer Clickable top level menu items if there
  are children items.
'''


class LoginMenu(Menu):
    name = _("Your Account")  # give the menu a name this is required.

    def get_nodes(self, request):
        """
        menus for all users or potential users to do account management
        """
        nodes = []

        nodes.append(NavigationNode(_("Your Account"), "", 1,
                                    attr={'visible_for_anonymous': False}))
        nodes.append(NavigationNode(_("Your Expo"),
                                    reverse('gbe:home'), 2, 1,
                                    attr={'visible_for_anonymous': False}))
        nodes.append(NavigationNode(_("Update Profile"),
                                    reverse('gbe:profile_update'), 3, 1,
                                    attr={'visible_for_anonymous': False}))
        nodes.append(NavigationNode(_("Logout"),
                                    reverse('gbe:logout'), 4, 1,
                                    attr={'visible_for_anonymous': False}))
        nodes.append(NavigationNode(_("Join Today"), "", 4,
                                    attr={'visible_for_authenticated': False}))
        nodes.append(NavigationNode(_("Register"),
                                    reverse('gbe:register'), 5, 4,
                                    attr={'visible_for_authenticated': False}))
        nodes.append(NavigationNode(_("Login"),
                                    reverse('gbe:login'), 6, 4,
                                    attr={'visible_for_authenticated': False}))

        return nodes

'''
  The special menu, I chose to separate them largely for modularity.
  Login and Special can all be in one function, but I thought the
  separation of areas was useful for readability.
'''


class SpecialMenu(Menu):
    name = _("Special")

    def get_nodes(self, request):
        """
        populate for users based on profile.
        Users must have special privileges to use this
        """
        nodes = []
        user = request.user
        if validate_perms(request, 'any', require=False):
            nodes.append(NavigationNode(_("Special"), "", 1))
            nodes.append(NavigationNode(_("Reporting"),
                                        reverse('reporting:report_list'),
                                        2, 1))
            for n,priv in enumerate(user.profile.special_privs,len(nodes)+1):
                if priv["url"]:
                    nodes.append(NavigationNode(priv["title"],
                                                priv["url"],
                                                n, 1))
        return nodes


menu_pool.register_menu(SpecialMenu)  # register the menu.
menu_pool.register_menu(LoginMenu)  # register the menu.
