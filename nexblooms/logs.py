# Logging Configurations

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/request.log',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 5,
            'encoding': 'utf-8',
            'formatter': 'verbose'
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(message)s (%(filename)s:%(lineno)s)',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
