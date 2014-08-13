# functions for connecting to ticketing code
import ticketing
from hashlib import md5
from datetime import datetime

def compute_submission(details):
    baseURL = '/ticketing/test/brownpaper/'
    token_string = ' '.join( map(str, [ details['user'], details['bid'], datetime.now()]))
    hash = md5(token_string).hexdigest()
    
    event = ticketing.models.BrownPaperEvents.objects.get(act_submission_event= details['is_submission_fee'])

    
    link = baseURL + 'ID-'+hash +'/'+event.bpt_event_id
    return {'link':link,
            'token':hash,
            'token_string':token_string}

