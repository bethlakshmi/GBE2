# 
# transaction_cron_job.py - Stand-Alone executable file for the Ticketing cron job.  
# This code is meant to be executed either directly from the command line, or from
# the linux cron server (or windows scheduled task server, or whatever).  
#
# Note:  the output from this function will create a bunch of "received native datetime"
# warnings.  I wasn't able to figure out how to suppress these.  Data imports just fine
# regardless.
#
# edited by mdb 8/18/2014
#
#

import sys, os
sys.path.append('./expo')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
from ticketing.models import *
from ticketing.brown_paper import *


print 'Executing Cron Job Script....'
print ''
count = process_bpt_order_list()
print '%s transactions added to the system.' % count
print ''









