from django.dispatch import (
    receiver,
    Signal
)
from django.db.models.signals import post_save

from gbe.models import AudioInfo
from django.core.management import call_command


def handle_unsync_audio_download(sender, **kwargs):
    '''Brutally kill all synced downloads if any audioinfo changes'''
    call_command('sync_audio_downloads',
                 unsync_all=True)

post_save.connect(handle_unsync_audio_download, sender=AudioInfo)
