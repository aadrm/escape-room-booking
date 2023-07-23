from .base import *

INSTALLED_APPS = INSTALLED_APPS + [
    "debug_toolbar",
]


MIDDLEWARE = MIDDLEWARE + [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]