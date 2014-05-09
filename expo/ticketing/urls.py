# 
# models.py - Contains Django code for defining the URL structure for ticketing
# edited by mdb 5/9/2014
#

from django.conf.urls import patterns, url
from ticketing import views

urlpatterns = patterns('', 
    url(r'^/?$', views.index, name='index'),
)



