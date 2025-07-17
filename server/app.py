from flask import Flask, request, jsonify, render_template_string
import datetime

app = Flask(__name__)

# In-memory status store (for demo; use a DB for production)
latest_status = {
    'last_watered': None,
    'next_scheduled': None,
    'rain_status': None,
    'system_time': None,
    'system_mm_last_7d': None,
    'rain_mm_last_7d': None,
    'message': 'No status received yet.'
}

@app.route('/api/status', methods=['POST'])
def update_status():
    data = request.json
    if not data:
        return jsonify({'error': 'No JSON received'}), 400
    latest_status.update(data)
    latest_status['system_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return jsonify({'ok': True})

@app.route('/')
def dashboard():
    html = '''
    <html><head><title>Watering System Dashboard</title>
    <style>
      body { font-family: Arial, sans-serif; background: #f4f8fb; color: #222; }
      h1 { color: #2a7ae2; text-align: center; }
      ul { background: #fff; padding: 2em; border-radius: 8px; box-shadow: 0 2px 8px #0001; max-width: 400px; margin: 2em auto; }
      li { margin-bottom: 1em; font-size: 1.1em; }
      @media (max-width: 600px) {
        ul { padding: 1em; max-width: 95vw; }
        h1 { font-size: 1.5em; }
      }
    </style>
    </head>
    <body>
    <h1>Watering System Status</h1>
    <ul>
      <li><b>Last Watered:</b> {{ status.last_watered }}</li>
      <li><b>Next Scheduled:</b> {{ status.next_scheduled }}</li>
      <li><b>Rain Status:</b> {{ status.rain_status }}</li>
      <li><b>System Time (server):</b> {{ status.system_time }}</li>
      <li><b>Watered by System (last 7d):</b> {{ status.system_mm_last_7d }} mm</li>
      <li><b>Rainfall (last 7d):</b> {{ status.rain_mm_last_7d }} mm</li>
      <li><b>Message:</b> {{ status.message }}</li>
    </ul>
    </body></html>
    '''
    return render_template_string(html, status=latest_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 