"""
Moonlight v2.0.2

Moonlight is a lightweight JSON-database for Python.

Github: https://github.com/De4oult/Moonlight/
"""

from .core.moonlight    import Moonlight
from .messages.logger   import Logger
from .config.config     import config
from .core.tools        import *
from .config.paths      import *
from .cli.cli           import *
from .api.api           import create_application
from .cli.decorators    import *
from .messages.messages import t
from .schemas.schemas   import Schema
from .schemas.queries   import Query, GetById
from .schemas.validate  import Validate