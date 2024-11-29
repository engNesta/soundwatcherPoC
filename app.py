from flask import Flask, render_template
from flask_socketio import SocketIO
from audio_capture import start_audio_stream_process

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Start the audio stream in the background and listen for WebSocket messages
    socketio.start_background_task(start_audio_stream_process, socketio)
    socketio.run(app, debug=True)
