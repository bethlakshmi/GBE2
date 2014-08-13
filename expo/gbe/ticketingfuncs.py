# functions for connecting to ticketing code
import ticketing
from hashlib import md5
from datetime import datetime

def compute_submission(details):
    baseURL = '/ticketing/test/brownpaper/'
    details['token_string'] =' '.join( map(str, [ details['user'], details['bid'], datetime.now()]))
    details['token']= md5(details['token_string']).hexdigest()
    event = ticketing.models.BrownPaperEvents.objects.get(act_submission_event= details['is_submission_fee'])
    details['event']=event
    details['link'] = baseURL + 'ID-'+details['token'] +'/'+event.bpt_event_id
    create_referral(details)
    return details


def create_referral(details):
    ref = ticketing.models.Referral()
    ref.user = details['user']
    ref.reference = details['token']
    ref.codeword = 'pistachio'
    ref.event=details['event']
    ref.save()
    details['reference'] = ref  #hang on to the pointer for now
