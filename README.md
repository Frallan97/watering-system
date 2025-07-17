# Raspberry Pi Plant Watering System

Automate your plant watering with a Raspberry Pi, relay, and weather-aware scheduling! This script controls a relay to power a watering pump, and can skip watering if it has rained in Lund, Sweden in the last 24 hours.

## Features
- **Flexible Scheduling:**
  - Water at a fixed frequency (e.g., every hour)
  - Or at specific times of day (e.g., 06:00,18:30)
- **Weather Integration:**
  - Uses OpenWeatherMap to check if it has rained in Lund, Sweden in the last 24 hours
  - Skips watering if rain is detected
- **Dry Run Mode:**
  - Test your setup without activating the relay
- **Robust Logging:**
  - Logs all actions, errors, and weather checks
- **Remote Monitoring:**
  - View system status from your phone via a web dashboard hosted on AWS Lightsail

## Requirements
- Raspberry Pi with GPIO support
- Relay module connected to GPIO pin 27 (default)
- Python 3
- Python packages: `RPi.GPIO`, `requests`, `Flask`

Install dependencies:
```sh
pip install requests RPi.GPIO Flask
```

## Setup
1. Connect your relay to GPIO pin 27 (or modify the script for a different pin).
2. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api).
3. Set your API key in the script (default is already set for Lund, Sweden).

## Usage
### Watering Script (on Raspberry Pi)
Run the script with desired arguments:

#### Water at a fixed frequency (default: every hour for 2 seconds)
```sh
python3 watering_script.py
```

#### Custom frequency and duration
```sh
python3 watering_script.py --duration 5 --frequency 7200
```
- Waters for 5 seconds every 2 hours.

#### Water at specific times (24-hour format, comma-separated)
```sh
python3 watering_script.py --duration 5 --times 06:00,18:30
```
- Waters at 06:00 and 18:30 every day.

#### Dry run (test mode, no relay activation)
```sh
python3 watering_script.py --dry-run --times 07:00
```

### Remote Monitoring (Web Dashboard)
#### 1. On your AWS Lightsail server:
- **Create a new Lightsail instance** (Ubuntu recommended)
- **Open firewall port 5000** (Networking tab > Add another > Custom > TCP > 5000)
- **SSH into your instance**
- **Install Python 3 and pip**
  ```sh
  sudo apt update && sudo apt install python3 python3-pip -y
  ```
- **Clone your repo and install requirements**
  ```sh
  git clone <your-repo-url>
  cd watering-system/server
  pip3 install -r requirements.txt
  ```
- **Run the server**
  ```sh
  python3 app.py
  ```
- (Optional) **Run as a service** (so it restarts on reboot):
  ```sh
  sudo nano /etc/systemd/system/watering-dashboard.service
  ```
  Paste:
  ```ini
  [Unit]
  Description=Watering Dashboard Flask App
  After=network.target

  [Service]
  User=ubuntu
  WorkingDirectory=/home/ubuntu/watering-system/server
  ExecStart=/usr/bin/python3 app.py
  Restart=always

  [Install]
  WantedBy=multi-user.target
  ```
  Then:
  ```sh
  sudo systemctl daemon-reload
  sudo systemctl enable watering-dashboard
  sudo systemctl start watering-dashboard
  ```
- **Set up your domain** to point to your Lightsail instance (Networking tab > Attach static IP > update DNS A record)
- (Recommended) **Set up HTTPS** (use a reverse proxy like Nginx + Certbot)

#### 2. On your Raspberry Pi:
- Edit `pi_status_reporter.py` and set `SERVER_URL` to your Lightsail domain or IP (e.g., `http://mydomain.com:5000/api/status`).
- Run the reporter:
```sh
python3 pi_status_reporter.py &
```
- This will send status updates every 5 minutes.

#### 3. View the Dashboard
- Open your browser (on your phone or computer) and go to `http://YOUR_DOMAIN_OR_IP:5000/`
- You’ll see the latest status from your watering system.

## Customizing the Dashboard (CSS)
The dashboard HTML is in `server/app.py` (in the `dashboard()` function). You can add or edit the `<style>` tag for custom CSS. Example:

```python
html = '''
<html><head><title>Watering System Dashboard</title>
<style>
  body { font-family: Arial, sans-serif; background: #f4f8fb; color: #222; }
  h1 { color: #2a7ae2; }
  ul { background: #fff; padding: 2em; border-radius: 8px; box-shadow: 0 2px 8px #0001; max-width: 400px; margin: 2em auto; }
  li { margin-bottom: 1em; font-size: 1.1em; }
</style>
</head>
<body> ...
```

Feel free to copy and paste this style block for a modern look!

## Arguments
- `--duration`   Watering duration in seconds (default: 2)
- `--frequency`  Watering frequency in seconds (default: 3600)
- `--dry-run`    Run without activating the relay (for testing)
- `--times`      Comma-separated list of military times (e.g., 06:00,18:30) to water instead of using frequency

## Weather Integration
- The script checks OpenWeatherMap for rain in Lund, Sweden in the last 24 hours.
- If the weather API fails, the script will water as if it did not rain (to avoid missing a watering cycle).

## Logging
- All actions and errors are logged with timestamps.
- Logs are printed to the console.

## Safety & Reliability
- GPIO is always cleaned up on exit.
- Script is robust to weather API failures.

## License
MIT 