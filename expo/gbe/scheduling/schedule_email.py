from gbe.models import ConferenceDay
from scheduler.idd import get_schedule
from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
import pytz


def schedule_email():
    target_day = date.today() + timedelta(days=1)
    personal_schedule = {}
    try:
        conf_day = ConferenceDay.objects.get(day=target_day)
    except DoesNotExist:
        return 0
    sched_resp = get_schedule(
        start_time=datetime.combine(
            target_day,
            time(0, 0, 0, 0, tzinfo=pytz.utc)),
        end_time=datetime.combine(
                target_day+timedelta(days=1), 
                time(0, 0, 0, 0, tzinfo=pytz.utc)))
    for item in sched_resp.schedule_items:
        if item.user in personal_schedule:
            personal_schedule[item.user] += [item]
        else:
            personal_schedule[item.user] = [item]
    return len(personal_schedule)
    
