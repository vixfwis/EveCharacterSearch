import os
import raven

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ['DJANGO_SECRET']
DEBUG = False
ALLOWED_HOSTS = ['evecharsearch.xyz']
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

RAVEN_CONFIG = {
    'dsn': os.environ['SENTRY_DSN'],
    'release': raven.fetch_git_sha(os.path.dirname(BASE_DIR)),
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARN'),
        },
    },
}

STATIC_ROOT = '/var/www/evecharsearch/static'
MEDIA_ROOT = '/var/www/evecharsearch/media'
