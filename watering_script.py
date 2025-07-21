import RPi.GPIO as GPIO
import time
import argparse
import requests
import logging
import json
import os
from datetime import datetime

# Configuration
RELAY_PIN = 27       # GPIO pin connected to the relay

# --- Weather Integration ---
OPENWEATHER_API_KEY = "f2c3205a623a624346a1ecd88bc64bd0"
LUND_COORDS = {"lat": 55.7047, "lon": 13.1910}

# --- Watering event logging ---
WATERING_LOG = 'watering_log.jsonl'
MM_PER_SECOND = 0.5  # Example: 0.5 mm per second of watering (adjust as needed)

def log_watering_event(duration):
    event = {
        'timestamp': datetime.now().isoformat(),
        'duration': duration,
        'mm_applied': duration * MM_PER_SECOND
    }
    with open(WATERING_LOG, 'a') as f:
        f.write(json.dumps(event) + '\n')
    logging.info(f"Logged watering event: {event}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Automated plant watering system with weather and rain check for Lund, Sweden. "
                    "Waters at specified military times (default: 06:00 and 18:00) for a set duration. Skips watering if it has rained in the last 24h."
    )
    parser.add_argument('--duration', type=int, default=20, help='Watering duration in seconds (default: 20)')
    parser.add_argument('--dry-run', action='store_true', help='Run without activating the relay (for testing)')
    parser.add_argument('--times', type=str, default='06:00,18:00', help='Comma-separated list of military times (e.g., 06:00,18:00) to water. Default: 06:00,18:00')
    return parser.parse_args()


def parse_times(times_str):
    """Parse a comma-separated string of military times into a list of (hour, minute) tuples."""
    import re
    if not times_str:
        return []
    times = []
    for t in times_str.split(','):
        t = t.strip()
        if not re.match(r'^\d{2}:\d{2}$', t):
            raise ValueError(f"Invalid time format: {t}. Use HH:MM (24-hour format).")
        hour, minute = map(int, t.split(':'))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError(f"Invalid time: {t}. Hour must be 00-23 and minute 00-59.")
        times.append((hour, minute))
    return times

def setup():
    GPIO.setmode(GPIO.BCM)        # Use BCM pin numbering
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Ensure relay is off initially (HIGH = off for active-low)

def flip_switch(duration, dry_run=False):
    if dry_run:
        logging.info(f"[DRY RUN] Would turn switch ON for {duration} seconds.")
        time.sleep(duration)
        logging.info("[DRY RUN] Would turn switch OFF.")
        return
    logging.info("Turning switch ON")
    GPIO.output(RELAY_PIN, GPIO.LOW)   # Turn relay ON
    time.sleep(duration)
    logging.info("Turning switch OFF")
    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn relay OFF
    log_watering_event(duration)

def cleanup():
    GPIO.cleanup()

def has_rained_last_24h(api_key=OPENWEATHER_API_KEY, coords=LUND_COORDS):
    """
    Returns True if it has rained in the last 24 hours in Lund, Sweden, using OpenWeatherMap One Call API.
    If the API call fails, returns False (proceed to water as if it did not rain) and logs a warning.
    """
    url = (
        f"https://api.openweathermap.org/data/2.5/onecall?lat={coords['lat']}&lon={coords['lon']}"
        f"&exclude=current,minutely,daily,alerts&appid={api_key}&units=metric"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        hourly = data.get("hourly", [])
        for hour in hourly[:24]:
            rain = hour.get("rain", {})
            if rain.get("1h", 0) > 0:
                return True
        return False
    except Exception as e:
        logging.warning(f"[Weather] Error fetching weather data: {e}. Proceeding to water as if it did not rain.")
        return False

if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("Starting watering system with settings: duration=%ds, dry_run=%s, times=%s", args.duration, args.dry_run, args.times)
    try:
        setup()
        times_list = []
        if args.times:
            try:
                times_list = parse_times(args.times)
            except ValueError as e:
                logging.error(str(e))
                exit(1)
        last_watered = set()
        while True:
            now = time.localtime()
            if times_list:
                # Water at specified times
                current_tuple = (now.tm_hour, now.tm_min)
                if current_tuple in times_list and current_tuple not in last_watered:
                    rain_checked = None
                    try:
                        rain_checked = has_rained_last_24h()
                    except Exception as e:
                        logging.warning(f"[Weather] Unexpected error during rain check: {e}. Proceeding to water as if it did not rain.")
                        rain_checked = False
                    if rain_checked:
                        logging.info("[Weather] It has rained in the last 24 hours in Lund. Skipping watering.")
                    elif args.dry_run:
                        logging.info("[DRY RUN] Skipping actual watering. Would have watered for %d seconds.", args.duration)
                        flip_switch(args.duration, args.dry_run)
                    else:
                        if rain_checked is False:
                            logging.info("[Weather] Proceeding to water (either no rain or weather check failed).")
                        flip_switch(args.duration, args.dry_run)
                    last_watered.add(current_tuple)
                # Reset last_watered at midnight
                if current_tuple == (0, 0):
                    last_watered.clear()
                time.sleep(30)  # Check every 30 seconds
            else:
                # Default: water at frequency
                rain_checked = None
                try:
                    rain_checked = has_rained_last_24h()
                except Exception as e:
                    logging.warning(f"[Weather] Unexpected error during rain check: {e}. Proceeding to water as if it did not rain.")
                    rain_checked = False
                if rain_checked:
                    logging.info("[Weather] It has rained in the last 24 hours in Lund. Skipping watering.")
                elif args.dry_run:
                    logging.info("[DRY RUN] Skipping actual watering. Would have watered for %d seconds.", args.duration)
                    flip_switch(args.duration, args.dry_run)
                else:
                    if rain_checked is False:
                        logging.info("[Weather] Proceeding to water (either no rain or weather check failed).")
                    flip_switch(args.duration, args.dry_run)
                logging.info(f"Waiting {args.frequency} seconds until next watering...")
                time.sleep(args.frequency)
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        cleanup()
        logging.info("GPIO cleanup done")
