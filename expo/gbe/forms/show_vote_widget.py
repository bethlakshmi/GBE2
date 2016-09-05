from django.forms.widgets import (
    MultiWidget,
    Select,
)
from gbe.models import (
    Show,
    ShowVote,
)
from gbe.functions import get_current_conference
from gbetext import vote_options


class ShowVoteWidget(MultiWidget):
    def __init__(self, attrs=None):
        shows = Show.objects.filter(
            conference=get_current_conference())
        show_choices = [(show.pk, show) for show in shows]
        _widgets = (Select(attrs=attrs, choices=show_choices),
                    Select(attrs=attrs, choices=vote_options))
        super(ShowVoteWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if not value:
            return (None, None)
        elif isinstance(value, ShowVote):
            return (value.show, value.vote)
        else:
            object = ShowVote.objects.get(pk=value)
            return (object.show, object.vote)

    def format_output(self, rendered_widgets):
        return "-".join(rendered_widgets)

    def value_from_datadict(self, data, files, name):
        vals = [
            widget.value_from_datadict(data, files, name + "_%s" % i)
            for i, widget in enumerate(self.widgets)]
        try:
            show_vote = ShowVote(show=Show.objects.get(pk=vals[0]),
                                 vote=vals[1])
            show_vote.save()
        except:
            return ""
        else:
            return show_vote
