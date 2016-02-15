from datetime import datetime

from gbe.duration import (
    Duration,
    DateTimeRange,
)
import nose.tools as nt
from unittest import TestCase

# unit tests for  DateTimeRange

def test_date_time_range_contains_datetime():
    moment = datetime(2015, 6, 6, 6, 0, 0)
    range = DateTimeRange(starttime=datetime(2015,1, 1),
                          duration=Duration(days=365))
    nt.assert_true(moment in range)

def test_date_time_range_contains_date_time_range():
    sub_range = DateTimeRange(duration=Duration(days=1),
                              endtime=datetime(2015, 5,5))
    containing_range = DateTimeRange(starttime=datetime(2015, 1, 1),
                                     endtime=datetime(2016, 1, 1))
    nt.assert_true(sub_range in containing_range)


def test_date_time_range_contains_date():
    date = date(2015, 6, 6)
    range = DateTimeRange(starttime=datetime(2015, 6, 1),
                          endtime=datetime(2015, 7, 1))
    nt.assert_true(date in range)
