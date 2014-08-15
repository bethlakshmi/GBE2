# functions to use from the admin in maintaining the gbe project


def rebuild_privileges():
    '''
    Reads the privilege set from gbetext and creates the correct groups to make these work
    '''
    from django.contrib.auth.models import Group
    from gbetext import special_privileges
    gs = [Group() for priv in special_privileges.keys()]
    for (g, p) in zip (gs, special_privileges.keys()):
        g.name=p
        for g in gs:
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
    usernames = ['jon', 'betty', 'hunter', 'scratch', 'marcus']
    return [User.objects.get(username=uname) for uname in usernames]


