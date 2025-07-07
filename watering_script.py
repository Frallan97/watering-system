import RPi.GPIO as GPIO
import time

# Configuration
RELAY_PIN = 27       # GPIO pin connected to the relay
ON_TIME = 2        # Time in seconds to keep the relay on

def setup():
    GPIO.setmode(GPIO.BCM)        # Use BCM pin numbering
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Ensure relay is off initially (HIGH = off for active-low)

def flip_switch():
    time.sleep(ON_TIME)
    print("Turning switch ON")
    GPIO.output(RELAY_PIN, GPIO.LOW)   # Turn relay ON
    time.sleep(ON_TIME)
    print("Turning switch OFF")
    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn relay OFF
    print("\n")

def cleanup():
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        setup()
        while True:
            flip_switch()
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        cleanup()
        print("GPIO cleanup done")
