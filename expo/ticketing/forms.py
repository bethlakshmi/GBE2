# 
# forms.py - Contains Django Forms for Ticketing based on forms.ModelForm
# edited by mdb 5/28/2014
#

from ticketing.models import *
from django import forms

class TicketItemForm(forms.ModelForm):
    class Meta:
        model=TicketItem
        fields = ['ticket_id', 'title', 'description', 'active', 'cost', 'linked_events']
        

'''
    ticket_id = models.CharField(max_length=30)
    title = models.CharField(max_length=50)
    description = models.TextField()
    active = models.BooleanField(default=False)
    cost = models.DecimalField(max_digits=20, decimal_places=2)
    linked_events = models.ManyToManyField('gbe.Event')
    datestamp = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(max_length=30)

    
class VendorBidForm(forms.ModelForm):
    help_times = forms.MultipleChoiceField(widget = forms.CheckboxSelectMultiple,
                                                choices = vendor_schedule_options)
    class Meta:
        model=Vendor
        fields = '__all__'
        labels = vendor_labels
        widgets = {'accepted': forms.HiddenInput(), 
                   'submitted' : forms.HiddenInput(),
                   'profile' : forms.HiddenInput()}
                   
'''

