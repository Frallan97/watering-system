import requests
import time
import datetime
import json
import os

SERVER_URL = 'http://YOUR_LIGHTSAIL_DOMAIN_OR_IP:5000/api/status'  # <-- Set this!
WATERING_LOG = 'watering_log.jsonl'

# For demo: mock rain. In production, fetch from weather API or log.
def get_rain_mm_last_7d():
    # TODO: Integrate with real rain data
    return 0.0

def get_system_mm_last_7d():
    now = datetime.datetime.now()
    total_mm = 0.0
    if not os.path.exists(WATERING_LOG):
        return 0.0
    with open(WATERING_LOG, 'r') as f:
        for line in f:
            try:
                event = json.loads(line)
                event_time = datetime.datetime.fromisoformat(event['timestamp'])
                if (now - event_time).days < 7:
                    total_mm += event.get('mm_applied', 0.0)
            except Exception:
                continue
    return total_mm

def get_status():
    now = datetime.datetime.now()
    return {
        'last_watered': now.strftime('%Y-%m-%d %H:%M:%S'),
        'next_scheduled': (now + datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'rain_status': 'No rain in last 24h',
        'system_mm_last_7d': get_system_mm_last_7d(),
        'rain_mm_last_7d': get_rain_mm_last_7d(),
        'message': 'System running normally.'
    }

if __name__ == '__main__':
    while True:
        status = get_status()
        try:
            resp = requests.post(SERVER_URL, json=status, timeout=10)
            print(f"[Reporter] Sent status: {status} | Response: {resp.status_code}")
        except Exception as e:
            print(f"[Reporter] Failed to send status: {e}")
        time.sleep(300)  # 5 minutes 