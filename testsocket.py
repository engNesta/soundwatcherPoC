from flask import Flask, render_template
from flask_socketio import SocketIO
import time

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

def test_socket_emission():
    """Simulate periodic WebSocket messages."""
    while True:
        socketio.emit('volume_update', {'volume': -42.0}, namespace='/')
        print("Emitting test volume: -42.0 dB")
        time.sleep(1)

if __name__ == '__main__':
    socketio.start_background_task(test_socket_emission)
    socketio.run(app, debug=True)
