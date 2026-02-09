from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'stoplight-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Background thread to cycle through stoplight states
def stoplight_cycle():
    states = [
        ('red',    7),   # red for ~7 seconds
        ('green',  6),   # green for ~6 seconds
        ('yellow', 3)    # yellow for ~3 seconds
    ]
    current_index = 0

    while True:
        color, duration = states[current_index]
        # Broadcast the active light to all connected clients
        socketio.emit('light_update', {'color': color})
        print(f"Active light: {color}")
        
        time.sleep(duration)
        
        # Move to next state
        current_index = (current_index + 1) % len(states)

# Start the background thread only once
thread = None
thread_lock = threading.Lock()

@app.route('/')
def index():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(stoplight_cycle)
    return render_template('index.html')

# Optional: handle client connection / disconnection
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Optionally send current state immediately on connect
    # (you could keep track of current color in a global var if desired)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)