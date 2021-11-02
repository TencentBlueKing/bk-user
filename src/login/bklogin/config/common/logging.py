# -*- coding: utf-8 -*-
import os

from . import BASE_DIR

# logging config
LOG_LEVEL = "INFO"
LOGGING_DIR = os.environ.get("PAAS_LOGGING_DIR") or os.path.join(os.path.dirname(BASE_DIR), "logs")
LOG_CLASS = "logging.handlers.RotatingFileHandler"
