# 
# models.py - Contains Django code for defining the URL structure for ticketing
# edited by mdb 5/9/2014
#

from django.conf.urls import patterns, url
from ticketing import views

urlpatterns = patterns('', 
    url('^$', views.index, name='index'),
    url(r'^ticket_items/?$', views.ticket_items, name='ticket_items'),
    url(r'^ticket_item_edit/?$', views.ticket_item_edit, name='ticket_item_edit'),
    url(r'^ticket_item_edit/(?P<item_id>\d+)/?$', views.ticket_item_edit, 
        name='ticket_item_edit')
    
)



