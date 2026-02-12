from flask import Flask, Response, render_template_string
from prometheus_client import Gauge, Counter, generate_latest, CONTENT_TYPE_LATEST
import random
import threading
import time

app = Flask(__name__)

# Prometheus metrics
random_values_gauge = Gauge('demo_app_random_values', 'Random values between 0 and 100')
clicks_total_counter = Counter('demo_app_clicks_total', 'Total number of clicks')
enabled_gauge = Gauge('demo_app_enabled', 'Whether the app is enabled (1) or disabled (0)')

# Initialize state
enabled_state = [0]  # Use list for mutable reference in closures

# Update random value every minute
def update_random_metric():
    while True:
        value = random.randint(0, 100)
        random_values_gauge.set(value)
        time.sleep(60)

threading.Thread(target=update_random_metric, daemon=True).start()

# Routes
@app.route('/')
def index():
    return render_template_string('''
        <html>
        <head>
            <title>Demo App with Prometheus</title>
            <style>
                button {
                    font-size: 18px;
                    padding: 10px 20px;
                    margin: 10px;
                    cursor: pointer;
                    border: none;
                    border-radius: 8px;
                    background-color: #007BFF;
                    color: white;
                    transition: background-color 0.3s ease;
                }
                button:active {
                    background-color: #0056b3;
                    transform: scale(0.98);
                }
                .clicked {
                    animation: clickFeedback 0.2s;
                }
                @keyframes clickFeedback {
                    0%   { transform: scale(1); }
                    50%  { transform: scale(0.95); }
                    100% { transform: scale(1); }
                }
            </style>
        </head>
        <body>
            <h1>Demo App with Prometheus Metrics</h1>
            <button onclick="sendClick(this, '/click')">Click Me!</button>
            <button onclick="sendClick(this, '/toggle')">Toggle Enabled</button>
            <p><a href="/metrics" target="_blank">View Metrics</a></p>

            <script>
                function sendClick(btn, endpoint) {
                    fetch(endpoint, { method: 'POST' })
                        .then(response => response.text())
                        .then(data => {
                            btn.classList.add('clicked');
                            setTimeout(() => btn.classList.remove('clicked'), 200);
                        })
                        .catch(err => console.error('Error:', err));
                }
            </script>
        </body>
        </html>
    ''')


@app.route('/click', methods=['POST'])
def click():
    clicks_total_counter.inc()
    return '', 204

@app.route('/toggle', methods=['POST'])
def toggle():
    if enabled_state[0] == 0:
        enabled_state[0] = 1
    else:
        enabled_state[0] = 0
    enabled_gauge.set(enabled_state[0])
    return '', 204  # No Content

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
