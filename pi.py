import numpy as np
import sounddevice as sd
from flask import Flask, render_template_string, request, jsonify
import threading
import time
import csv

# -----------------------
# Configuration
# -----------------------
FS = 48000      # Sampling rate
N = 1024        # Block size for Goertzel
LOG_FILE = "frequency_log.csv"

# -----------------------
# Global State
# -----------------------
target_frequency = 1000  # default frequency
current_magnitude = 0.0
logging_active = False
state_lock = threading.Lock()

# -----------------------
# Goertzel Function
# -----------------------
def goertzel(samples, f_target, fs):
    """Compute magnitude at f_target using Goertzel"""
    N = len(samples)
    # Hann window
    window = np.hanning(N)
    samples = samples * window

    omega = 2.0 * np.pi * f_target / fs
    coeff = 2.0 * np.cos(omega)
    s_prev = 0.0
    s_prev2 = 0.0
    for x in samples:
        s = x + coeff * s_prev - s_prev2
        s_prev2 = s_prev
        s_prev = s
    power = s_prev*2 + s_prev2*2 - coeff*s_prev*s_prev2
    magnitude = np.sqrt(power)
    return magnitude

# -----------------------
# Audio Thread
# -----------------------
def audio_thread():
    global current_magnitude
    while True:
        samples = sd.rec(N, samplerate=FS, channels=1, dtype='float32')
        sd.wait()
        samples = samples[:,0]
        with state_lock:
            freq = target_frequency
        magnitude = goertzel(samples, freq, FS)
        with state_lock:
            current_magnitude = magnitude
        time.sleep(0.01)  # small delay to avoid CPU hogging

# -----------------------
# Logging Thread
# -----------------------
def logging_thread():
    while True:
        with state_lock:
            log_active = logging_active
            mag = current_magnitude
        if log_active:
            with open(LOG_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), mag])
        time.sleep(1)  # log every 1 second

# -----------------------
# Flask Web App
# -----------------------
app = Flask(_name_)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Frequency Magnitude Monitor</title>
<script>
function updateMagnitude(){
    fetch('/magnitude')
    .then(response => response.json())
    .then(data => {
        document.getElementById('mag').innerText = data.magnitude.toFixed(2);
    });
}
function setFrequency(){
    let freq = parseFloat(document.getElementById('freq').value);
    fetch('/set_frequency', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({frequency: freq})
    });
}
function startLogging(){
    fetch('/start_logging');
}
function stopLogging(){
    fetch('/stop_logging');
}
setInterval(updateMagnitude, 25);
</script>
</head>
<body>
<h1>Frequency Magnitude Monitor</h1>
<label>Frequency (Hz): <input type="number" id="freq" value="1000"></label>
<button onclick="setFrequency()">Set Frequency</button>
<p>Current Magnitude: <span id="mag">0</span></p>
<button onclick="startLogging()">Start Logging</button>
<button onclick="stopLogging()">Stop Logging</button>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/magnitude')
def magnitude():
    with state_lock:
        mag = current_magnitude
    return jsonify({'magnitude': mag})

@app.route('/set_frequency', methods=['POST'])
def set_frequency():
    global target_frequency
    data = request.get_json()
    with state_lock:
        target_frequency = float(data['frequency'])
    return jsonify({'status':'ok'})

@app.route('/start_logging')
def start_logging():
    global logging_active
    with state_lock:
        logging_active = True
    return jsonify({'status':'logging_started'})

@app.route('/stop_logging')
def stop_logging():
    global logging_active
    with state_lock:
        logging_active = False
    return jsonify({'status':'logging_stopped'})

# -----------------------
# Main
# -----------------------
if _name_ == '_main_':
    # Start threads
    threading.Thread(target=audio_thread, daemon=True).start()
    threading.Thread(target=logging_thread, daemon=True).start()
    # Start Flask server
    app.run(host='0.0.0.0', port=5000, debug=False)
