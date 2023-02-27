# Logging for sentry
As we are moving towards CICD exceptions should be logged as far as possible. This will allow us to monitor all exceptions in Sentry, allowing for speedier bugfixes and crisis handling.

## Log Levels


# Logging in evco_os application
Please refer to evcoos/settings/defaults.py for the comprehensive list of logs. 
- some are for specific processes, e.g. `charge-log` for charging
- some are for modules, e.g. `cportal` for our overall customer portal
- for more on naming, please refer to: https://docs.djangoproject.com/en/4.1/howto/logging/#naming-loggers

## example for logging CRUD services:
---
```python
import logging
logger = logging.getLogger('crud-log')

def testFunc():
    # normal logs
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")

    # log exception
    try:
        1/0
    except Exception as e:
        logger.exception(e) 
        # OR
        logger.exception("a custom message that still prints the traceback")

```

## example for logging in a module:
---
e.g. 'asset' log used in asset.views.AssetView 
```python
import logging
logger = logging.getLogger(__name__) 
# using __name__ will send back to asset log regardless of namespace, as long as under 'asset'

def testFunc():
    # normal logs
    # see above for this snippet

   # log exception 
    try:
        1/0
    except Exception as e:
        logger.exception(e) 
        # OR
        logger.exception("a custom message that still prints the traceback")
```
