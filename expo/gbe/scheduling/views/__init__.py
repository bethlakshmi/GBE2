# New Event Creation
from event_wizard_view import EventWizardView
from class_wizard_view import ClassWizardView
from ticketed_event_wizard_view import TicketedEventWizardView

# Brand new edit (will deprecate make_occurrence)
from edit_event_view import EditEventView

# Old but Refactored Event Editing/Creation/Allocation
from copy_occurrence_view import CopyOccurrenceView
from create_event_view import CreateEventView
from make_occurrence_view import MakeOccurrenceView
from manage_vol_ops_view import ManageVolOpsView
from allocate_worker_view import AllocateWorkerView

from manage_events_view import ManageEventsView

# Public features
from show_calendar_view import ShowCalendarView
from set_favorite_view import SetFavoriteView
from list_events_view import ListEventsView
from event_detail_view import EventDetailView
