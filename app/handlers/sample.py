from flask.ext.socketio import SocketIO, emit

@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': 'got it!'})