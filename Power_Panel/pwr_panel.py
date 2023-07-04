#!/usr/bin/env python
import RPi.GPIO as GPIO
import os
import time
import threading
import struct
import smbus
import sys
import pygame
import signal

# Set up GPIO mode and pins
PLD = 6
BUZZER = 20
power_btn = 16
standby_led = 12
warning_led = 25
reboot_pin = 5
shutdown_pin = 26
I2C_ADDR = 0x36
GPIO.setwarnings(False)  # Disable GPIO warnings
GPIO.setmode(GPIO.BCM)
GPIO.setup(power_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(warning_led, GPIO.OUT)
GPIO.setup(standby_led, GPIO.OUT)
GPIO.setup(PLD, GPIO.IN)
GPIO.setup(BUZZER, GPIO.OUT)
GPIO.setup(reboot_pin, GPIO.OUT)
GPIO.setup(shutdown_pin, GPIO.OUT)
GPIO.setwarnings(False)

GPIO.output(standby_led, 1)
GPIO.output(warning_led, 0)
GPIO.output(BUZZER, 0)

# Driver modifiers
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"
# Initialize Pygame
pygame.init()
# Set display dimensions and icons
win_width = 10
win_height = 10
pygame.display.set_caption("Battery Monitor")
screen = pygame.display.set_mode((win_width, win_height), 16)

def flash_warning_led():
    for _ in range(18):  # Flash the warning LED 20 times
        GPIO.output(warning_led, 1)
        time.sleep(0.25)
        GPIO.output(warning_led, 0)
        time.sleep(0.25)

def hw_buzzer():
    for _ in range(40):  # Buzz the buzzer 40 times
        GPIO.output(BUZZER, 1)
        time.sleep(0.25)
        GPIO.output(BUZZER, 0)
        time.sleep(0.25)

def button_callback(channel):
    button_press_time = time.time()
    while GPIO.input(power_btn) == GPIO.LOW:
        pass
    button_release_time = time.time()
    button_duration = button_release_time - button_press_time
    if 0.25 < button_duration < 3:
        print("Button pressed for {:.2f} seconds. System will reboot in 10 seconds...".format(button_duration))
        GPIO.output(standby_led, 0)
        flash_warning_led()  # Flash the reboot LED before rebooting
        time.sleep(0.1)  # Delay before initiating the reboot command
        GPIO.output(warning_led, 0)  # Ensure the reboot LED is turned OFF
        GPIO.output(reboot_pin, 1)
        time.sleep(0.5)
        GPIO.output(reboot_pin, 0)
    elif button_duration > 3:
        print("Button pressed for {:.2f} seconds. System will shutdown in 15 seconds...".format(button_duration))
        GPIO.output(standby_led, 0)
        flash_warning_led()  # Flash the reboot LED before rebooting
        time.sleep(0.1)  # Delay before initiating the reboot command
        GPIO.output(warning_led, 0)  # Ensure the reboot LED is turned OFF
        time.sleep(0.1)
        GPIO.output(shutdown_pin, 1)
        time.sleep(5)
        GPIO.output(shutdown_pin, 0)
    time.sleep(1)

def readVoltage(bus):
    address = I2C_ADDR
    read = bus.read_word_data(address, 2)
    swapped = struct.unpack("<H", struct.pack(">H", read))[0]
    voltage = swapped * 1.25 / 1000 / 16
    return voltage

def readCapacity(bus):
    address = I2C_ADDR
    read = bus.read_word_data(address, 4)
    swapped = struct.unpack("<H", struct.pack(">H", read))[0]
    capacity = swapped / 256
    return capacity

def lowBattery(bus):
    while True:
        voltage = readVoltage(bus)
        if voltage < 3.50:
            print("Plug in the power supply soon.\nSave your work in case of battery shutdown")
            hw_buzzer()
        time.sleep(1)  # Check battery level every second

def lifeSaver(bus):
    # Check battery status
    capacity = readCapacity(bus)
    voltage = readVoltage(bus)
    if capacity < 20 and voltage < 3.52:
        GPIO.output(standby_led, 0)
        flash_warning_led()
        time.sleep(0.1)
        GPIO.output(warning_led, 0)  # Ensure the reboot LED is turned OFF
        GPIO.output(shutdown_pin, 1)
        time.sleep(0.5)
        GPIO.output(shutdown_pin, 0)

def sigterm_thread():
    signal.sigwait([signal.SIGTERM])
    # Perform cleanup actions here

# Add the sigterm_thread to the main function
def main():
    # Create a bus object for I2C communication
    bus = smbus.SMBus(1)

    # Start the lowBattery thread
    lowBatteryThread = threading.Thread(target=lowBattery, args=(bus,))
    lowBatteryThread.start()

    # Start the SIGTERM thread
    sigtermThread = threading.Thread(target=sigterm_thread)
    sigtermThread.start()

    # Check for button press
    GPIO.add_event_detect(power_btn, GPIO.FALLING, callback=button_callback, bouncetime=200)

    # Main loop
    try:
        while True:
            # Check battery status periodically
            lifeSaver(bus)

            time.sleep(1)

    except KeyboardInterrupt:
        GPIO.remove_event_detect(power_btn)  # Remove event detection for power_btn
        GPIO.cleanup()
        lowBatteryThread.join()
        
    finally:
        GPIO.remove_event_detect(power_btn)
        GPIO.cleanup()

    # Wait for the SIGTERM thread to finish
    sigtermThread.join()

if __name__ == "__main__":
    main()