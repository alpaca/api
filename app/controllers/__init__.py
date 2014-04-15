# -*- coding: utf-8 -*-

from .. import app
from flask.ext.restful import Api

api = Api(app)

from app.controllers import *