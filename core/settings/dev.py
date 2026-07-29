from .base import *  # noqa

DEBUG = True

# Show SQL queries in development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'colored': {
            'format': '\033[92m{levelname}\033[0m {asctime} \033[94m{module}\033[0m {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
        },
    },
    'root': {'handlers': ['console'], 'level': 'DEBUG'},
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Shows SQL queries
            'propagate': False,
        },
        'apps': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'apps.shared': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}
