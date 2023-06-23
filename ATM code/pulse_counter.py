import RPi.GPIO as GPIO
import time
import threading

# Set GPIO mode and pin numbers
GPIO.setmode(GPIO.BCM)
pulse_pin = 17
trigger_pin = 27

# Initialize pulse counter
pulse_count = 0
counting = True

# Define callback function for pulse detection with debounce
def count_pulses(channel):
    global pulse_count
    pulse_count += 1

# Set up GPIO pins for input and output
GPIO.setup(pulse_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(trigger_pin, GPIO.OUT)

# Turn on trigger pin initially
GPIO.output(trigger_pin, GPIO.HIGH)

# Add event detection on rising edge with debounce time
debounce_time = 0.05  # Adjust this value as needed
GPIO.add_event_detect(pulse_pin, GPIO.RISING, callback=count_pulses, bouncetime=int(debounce_time * 1000))

# Function to stop the pulse counter
def stop_counter():
    global counting
    counting = False
    GPIO.cleanup()

# Function to display pulse count
def display_count():
    while counting:
        print("Pulse count:", pulse_count)
        time.sleep(0.05)  # Wait for 50ms

# Main thread to handle user input
try:
    print("Press Enter to stop the pulse counter.")
    pulse_counter_thread = threading.Thread(target=display_count)
    pulse_counter_thread.start()
    input()
    stop_counter()
    pulse_counter_thread.join()
except KeyboardInterrupt:
    stop_counter()

# Save pulse count to a txt file
with open('pulse_count.txt', 'w') as file:
    file.write(str(pulse_count))
