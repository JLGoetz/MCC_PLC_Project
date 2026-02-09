from flask import Flask, render_template, Response
import time
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def event_stream():
    """Generator that yields the currently active light every few seconds"""
    states = ['red', 'green', 'yellow']  # order: red → green → yellow → repeat
    current_index = 0

    while True:
        active_light = states[current_index]
        
        # Send the active light color
        yield f"data: {active_light}\n\n"
        
        # Simulate realistic timing
        if active_light == 'red':
            sleep_time = 7    # red stays longest
        elif active_light == 'green':
            sleep_time = 6
        else:  # yellow
            sleep_time = 3
        
        time.sleep(sleep_time)
        
        # Move to next state
        current_index = (current_index + 1) % len(states)

@app.route('/stream')
def stream():
    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

if __name__ == '__main__':
    app.run(debug=True, threaded=True)