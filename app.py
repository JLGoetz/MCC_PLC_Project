from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'stoplight-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Statistics for percentages
cycle_count = 0
total_red_time = 0.0
total_yellow_time = 0.0
total_green_time = 0.0
stats_lock = threading.Lock()

def stoplight_cycle():
    global cycle_count, total_red_time, total_yellow_time, total_green_time

    states = [
        {'color': 'red',    'duration': 7},
        {'color': 'green',  'duration': 6},
        {'color': 'yellow', 'duration': 3}
    ]
    current_index = 0

    while True:
        state = states[current_index]
        color = state['color']
        duration = state['duration']

        # Broadcast current light
        socketio.emit('light_update', {'color': color})

        # Wait for the duration
        time.sleep(duration)

        # Update stats after the phase ends
        with stats_lock:
            if color == 'red':
                total_red_time += duration
            elif color == 'yellow':
                total_yellow_time += duration
            elif color == 'green':
                total_green_time += duration

            # After yellow ends → full cycle completed
            if color == 'yellow':
                cycle_count += 1
                # Send updated stats
                total_time = total_red_time + total_yellow_time + total_green_time
                if total_time > 0:
                    socketio.emit('stats_update', {
                        'cycle': cycle_count,
                        'red_pct': round((total_red_time / total_time) * 100, 1),
                        'yellow_pct': round((total_yellow_time / total_time) * 100, 1),
                        'green_pct': round((total_green_time / total_time) * 100, 1)
                    })

        current_index = (current_index + 1) % len(states)

# Background thread management
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

@socketio.on('reset')
def handle_reset():
    global cycle_count, total_red_time, total_yellow_time, total_green_time
    with stats_lock:
        cycle_count = 0
        total_red_time = 0.0
        total_yellow_time = 0.0
        total_green_time = 0.0
    socketio.emit('stats_update', {
        'cycle': 0,
        'red_pct': 0.0,
        'yellow_pct': 0.0,
        'green_pct': 0.0
    })
    print("Statistics and cycle reset")

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)