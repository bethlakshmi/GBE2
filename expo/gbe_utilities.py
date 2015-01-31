# functions to use from the admin in maintaining the gbe project


def create_standard_rehearsal_slots(shows):
    '''
    caller has to find the shows (as scheduler.Events, usually first 4 listed in .objects.all)
    '''
    import gbe.models as conf
    import scheduler.models as sched
    from datetime import timedelta
    hour = timedelta(seconds = 3600)
    for show in shows:
        for i in range (1,4):
            ge = conf.GenericEvent(title = '%s: Tech Rehearsal' %str(show), type = 'Rehearsal Slot', duration=3600) 
            ge.save()
            child = sched.Event(eventitem=ge, starttime = show.starttime- ( i  * hour))
            child.save()
            child.set_location(show.location)
            child.save()
            ec = sched.EventContainer(parent_event = show, child_event=child)
            ec.save()


def rebuild_privileges():
    '''
    Reads the privilege set from gbetext and creates the correct groups to make these work
    '''
    from django.contrib.auth.models import Group
    from gbe.special_privileges import special_privileges
    for p in special_privileges.keys():
        g = Group()
        g.name=p
        g.save()
    

def restore_base_users():
    '''
    Reads the pickled set of core users and inserts them into the db
    Use with fresh DB only, not tested with populated db. 
    '''
    import pickle
    base_users = pickle.load(open('pickles/base_users.pkl'))
    for user in base_users:
        user.save()


def restore_room_set():
    '''
    Restore serialized room set from disk to DB
    '''
    import pickle
    rooms = pickle.load(open('pickles/rooms.pkl'))
    for room in rooms:
	room.save()

def store_room_set():
    '''
    Serialize the current room set for later restoration
    '''	
    import pickle
    from gbe.models import Room
    rooms = list( Room.objects.all())
    pickle.dump(rooms, open('pickles/rooms.pkl','w'))

def store_base_users(base_users):
    '''
    Given a list of base users, store them for later use. Don't know if this will 
    restore passwords, we'll find out when we unpickle them I guess. 

    Note: it is the user's responsibility to assemble a list of base_users for this 
    function to store. The next function will help with this
    '''
    import pickle
    pickle.dump(base_users, open('pickles/base_users/pkl', 'w'))
    

def select_base_users():
    '''
    Find a set of users corresponding to these usernames and return the list of Users
    '''
    from django.contrib.auth.models import User
    usernames = ['jon', 'betty', 'hunter', 'scratch', 'gbeadmin']
    return [User.objects.get(username=uname) for uname in usernames]


