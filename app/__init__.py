# -*- coding: utf-8 -*-

from flask import Flask
from . import settings
from . import environment

# Allow importing libraries from lib folder

app = Flask(__name__)
app.config.from_object(settings.config)

from . import models
from . import controllers
from . import routes
from . import handlers

# Set up logging

import logging

if not app.debug:
    app.logger.setLevel(logging.INFO)
    settings.log_handler.setLevel(logging.INFO)
else:
    app.logger.setLevel(logging.DEBUG)
    settings.log_handler.setLevel(logging.DEBUG)

app.logger.addHandler(settings.log_handler)