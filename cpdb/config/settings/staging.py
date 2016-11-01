from .common import *  # NOQA

DEBUG = False


INSTALLED_APPS += ('corsheaders',)
MIDDLEWARE_CLASSES += (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware')

CORS_ORIGIN_WHITELIST = (
    'ms.cpdp.co',
    )

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/pyenv/versions/cpdb/emails'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'error-file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/pyenv/versions/cpdb/logs/django-error.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 10,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['error-file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
