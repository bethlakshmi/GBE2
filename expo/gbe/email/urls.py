from django.conf.urls import (
    patterns,
    url,
)

from gbe.email.views import (
    EditTemplateView,
    ListTemplateView,
)

# NOTE: in general, url patterns should end with '/?$'. This
# means "match the preceding patter, plus an optional final '?',
# and no other characters following. So '^foo/?$' matches on
# "foo" or "foo/", but not on "foo/bar" or "foo!".
# Which is what we usually want.

urlpatterns = patterns(
    '',
    url(r'^email/edit_template/(?P<template_name>[\w|\W]+)/?$',
        EditTemplateView.as_view(), name='edit_template'),
    url(r'^email/list_template/?$',
        ListTemplateView.as_view(), name='list_template'),
)
