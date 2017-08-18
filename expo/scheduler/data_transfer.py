

class Person(object):
    def __init__(self,
                 booking_id=None,
                 user=None,
                 public_id=None,
                 role=None,
                 label=None,
                 worker=None):
        if worker:
            self.role = worker.role
            self.user = worker._item.as_subtype.user_object
            self.public_id = worker._item.pk
        else:
            self.user = user
            self.public_id = public_id
            self.role = role

        self.booking_id = booking_id
        self.label = label


class Warning(object):
    def __init__(self,
                 code=None,
                 user=None,
                 occurrence=None,
                 details=None):
        self.code = code
        self.user = user
        self.occurrence = occurrence
        self.details = details


class Error(object):
    def __init__(self,
                 code=None,
                 details=None):
        self.code = code
        self.details = details


class OccurrenceResponse(object):
    def __init__(self,
                 occurrence=None,
                 warnings=[],
                 errors=[]):
        self.occurrence = occurrence
        self.warnings = warnings
        self.errors = errors


class OccurrencesResponse(object):
    def __init__(self,
                 occurrences=[],
                 warnings=[],
                 errors=[]):
        self.occurrences = occurrences
        self.warnings = warnings
        self.errors = errors
