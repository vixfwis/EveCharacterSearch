from os import getenv
from .base import *
if getenv('DJANGO_DEV'):
    from .dev import *
else:
    from .prod import *
