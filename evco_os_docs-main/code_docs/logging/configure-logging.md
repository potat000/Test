# Logging configuration
Example `LOGGING` variable:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'db_log': {
            'level': 'INFO',
            'class': 'django_db_logger.db_log_handler.DatabaseLogHandler'
        },
        'sentry': {
            'level': 'INFO',
            'class': 'logging.StreamHandler', # can be filehandler also
        },
    },
    #####################
    ## BEGIN SECTION 1 ##
    #####################
    'loggers': {
        'evcoos-system-log': {
            'handlers': ['db_log'],
        },
        'util-log': { # for util services logging
            'handlers': ['sentry'],
        },
        'crud-log': { # for crud services logging
            'handlers': ['sentry'],
        },
        'charging-log': { # for charging-related logging
            'handlers': ['sentry'],
        },
    # end #
    
    #####################
    ## BEGIN SECTION 2 ##
    #####################
        # cportal
        'cportal': {
            'handlers': ['sentry'],
        },
        'cportal.views': {
            'handlers': ['sentry'],
            'propagate': False,
        },
        'cportal.interfaces': {
            'handlers': ['sentry'],
            'propagate': False,
        },
    # end #

    #####################
    ## BEGIN SECTION 3 ##
    #####################
        # servers
        'apisvr': {
            'handlers': ['sentry'],
        },
        'ocppsvr': {
            'handlers': ['sentry'],
        },
        'asset': {
            'handlers': ['sentry'],
        },
    # end #
    }
}
```

# Section breakdown

## Section 1: Custom Loggers
---
These are custom logs that are used across modules for common processes, or processes that span across modules. Why this matters is explained in the next section.
```python
    ...
    'loggers': {
        'evcoos-system-log': {
            'handlers': ['db_log'],
        },
        'util-log': { # for util services logging
            'handlers': ['sentry'],
        },
        'crud-log': { # for crud services logging
            'handlers': ['sentry'],
        },
        'charging-log': { # for charging-related logging
            'handlers': ['sentry'],
        },
    ...
```
## Section 2: Cportal Logger
---
Please refer to this short [helpful resource: Use logger namespacing](https://docs.djangoproject.com/en/4.1/howto/logging/#use-logger-namespacing)

Sometimes modules are so large that it makes sense to have separate logs for different submodules. In our case, we want `cportal/views` to have a different log from `cportal/interfaces`
```python
    ...
    # cportal
        'cportal': {
            'handlers': ['sentry'],
        },
        'cportal.views': {
            'handlers': ['sentry'],
            'propagate': False,
        },
        'cportal.interfaces': {
            'handlers': ['sentry'],
            'propagate': False,
        },
    ...
```
## Section 3: specific module loggers
---
Following the logic of the previous session, for modules that are critical and (mostly) self-contained
```python
    ...
    # servers
        'apisvr': {
            'handlers': ['sentry'],
        },
        'ocppsvr': {
            'handlers': ['sentry'],
        },
        'asset': {
            'handlers': ['sentry'],
        },
    ...
```