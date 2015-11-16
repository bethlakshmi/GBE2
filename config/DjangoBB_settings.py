

# HAYSTACK settings, for DjangoBB_Forum
HAYSTACK_DEFAULT_OPERATOR = 'OR'
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': '/vagrant/expo/whoosh/whoosh_index',
        'TIMEOUT': 60 * 5,
        'INCLUDE_SPELLING': True,
        'BATCH_SIZE': 100,
        'EXCLUDED_INDEXES': ['thirdpartyapp.search_indexes.BarIndex'],
    },
    'autocomplete': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': '/vagrant/expo/whoosh_index',
        'STORAGE': 'file',
        'POST_LIMIT': 128 * 1024 * 1024,
        'INCLUDE_SPELLING': True,
        'BATCH_SIZE': 100,
        'EXCLUDED_INDEXES': ['thirdpartyapp.search_indexes.BarIndex'],
    },
#    'slave': {
#        'ENGINE': 'xapian_backend.XapianEngine',
#        'PATH': '/home/search/xapian_index',
#        'INCLUDE_SPELLING': True,
#        'BATCH_SIZE': 100,
#        'EXCLUDED_INDEXES': ['thirdpartyapp.search_indexes.BarIndex'],
#    },
    'db': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
        'EXCLUDED_INDEXES': ['thirdpartyapp.search_indexes.BarIndex'],
    }
}
