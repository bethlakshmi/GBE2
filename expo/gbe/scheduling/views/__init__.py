# New Event Creation
from event_wizard_view import EventWizardView
from class_wizard_view import ClassWizardView
from rehearsal_wizard_view import RehearsalWizardView
from staff_area_wizard_view import StaffAreaWizardView
from ticketed_event_wizard_view import TicketedEventWizardView
from volunteer_wizard_view import VolunteerWizardView

# Brand new edit (will deprecate make_occurrence)
from manage_vol_wizard_view import ManageVolWizardView
from edit_event_view import EditEventView
from edit_staff_area_view import EditStaffAreaView
from copy_collections_view import CopyCollectionsView
from copy_occurrence_view import CopyOccurrenceView
from copy_staff_area_view import CopyStaffAreaView

# Old but Refactored Event Editing/Creation/Allocation
from make_occurrence_view import MakeOccurrenceView
from manage_vol_ops_view import ManageVolOpsView
from allocate_worker_view import AllocateWorkerView

from manage_events_view import ManageEventsView
from delete_event_view import DeleteEventView

# Public features
from show_calendar_view import ShowCalendarView
from set_favorite_view import SetFavoriteView
from list_events_view import ListEventsView
from event_detail_view import EventDetailView
from eval_event_view import EvalEventView
