# 
# models.py - Contains Django code for the built-in Admin webpage
# edited by mdb 6/6/2014
#

from django.contrib import admin
from ticketing.models import *

# Register your models here.

admin.site.register( BrownPaperSettings )
admin.site.register( BrownPaperEvents )
admin.site.register( TicketItem )
admin.site.register( Purchaser )

