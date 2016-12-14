#!/usr/bin/env python

#
# transaction_cron_job.py - Stand-Alone executable file
#     for the Ticketing cron job.
# This code is meant to be executed either directly from the
#     command line, or from
# the linux cron server (or windows scheduled task server, or whatever).
#
# Note:  the output from this function will create a bunch of
#     "received native datetime" warnings.  I wasn't able to figure
#     out how to suppress these.  Data imports just fine regardless.
#
# edited by mdb 8/18/2014
#
# Needed on webfactional installation in place of current lines 19 & 20
# sys.path.append('/home/gbeadmin/webapps/gbetest/expo')
# os.environ['DJANGO_SETTINGS_MODULE'] = 'expo.settings'

import sys, os
sys.path.append('./expo')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from expo.gbe_logging import logger
from django.conf import settings
from ticketing.models import *
from ticketing.brown_paper import *


logger.info('Executing Cron Job Script....')
count = process_bpt_order_list()
logger.info('%s transactions added to the system.' % count)









