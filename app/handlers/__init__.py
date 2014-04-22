from .. import app

from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit

socketio = SocketIO(app)

__all__ = ['sample']

# import the handlers you need
# from handlers import *