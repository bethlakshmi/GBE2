import pytz
from datetime import datetime, time
from scheduler.idd.data_transfer import Person


def get_single_role(data, roles=None):
    people = []
    if not roles:
        roles = [('teacher', 'Teacher'),
                 ('moderator', 'Moderator'),
                 ('staff_lead', 'Staff Lead')]
    for role_key, role in roles:
        if data[role_key]:
            people += [Person(
                user=data[role_key].workeritem.as_subtype.user_object,
                public_id=data[role_key].workeritem.pk,
                role=role)]
    return people


def get_multi_role(data, roles=None):
    people = []
    if not roles:
        roles = [('panelists', 'Panelist')]
    for role_key, role in roles:
        if len(data[role_key]) > 0:
            for worker in data[role_key]:
                people += [Person(
                    user=worker.workeritem.as_subtype.user_object,
                    public_id=worker.workeritem.pk,
                    role=role)]
    return people

def get_start_time(data):
    day = data['day'].day
    time_parts = map(int, data['time'].split(":"))
    starttime = time(*time_parts, tzinfo=pytz.utc)
    return datetime.combine(day, starttime)
