from django.forms.widgets import (
    MultiWidget,
    Select,
)
from gbe.models import (
    Show,
    ShowVote,
)
from gbetext import vote_options


class ShowVoteWidget(MultiWidget):
    def __init__(self, attrs=None):    
        _widgets = [Select(attrs=attrs),
                    Select(attrs=attrs, choices=vote_options)]
        super(ShowVoteWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if not value:
            return (None, None)
        elif isinstance(value, ShowVote):
            return (value.show.pk, value.vote)
        else:
            object = ShowVote.objects.get(pk=value)
            return (object.show.pk, object.vote)

    def format_output(self, rendered_widgets):
        return "".join(rendered_widgets)

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
