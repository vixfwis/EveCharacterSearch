import os

SECRET_KEY = 'something like secret key i guess'
DEBUG = True
ALLOWED_HOSTS = ['*']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'formatters': {
        'simple': {
            'format': '%(levelname)s | %(asctime)s | %(module)s | %(message)s'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'charsearch_app': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}
