#!/usr/bin/env python
import struct
import smbus
import sys
import time
import threading
import RPi.GPIO as GPIO
import pygame
import os
import tkinter as tk

# Driver modifiers
os.environ["SDL_AUDIODRIVER"] = "dummy"

# Set up GPIO mode and pins
PLD_PIN = 6
BUZZER_PIN = 20
power_btn = 16
power_led = 12
reboot_led = 25

# Global settings
# GPIO26 is for x728 V2.1/V2.2/V2.3, GPIO13 is for X728 v2.0/v1.2/v1.3
GPIO_PORT = 26
I2C_ADDR = 0x36

GPIO.setwarnings(False)  # Disable GPIO warnings
GPIO.setmode(GPIO.BCM)
GPIO.setup(power_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(reboot_led, GPIO.OUT)
GPIO.setup(power_led, GPIO.OUT)
GPIO.setup(PLD_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Set up Pygame display
win_width = 100
win_height = 390

pygame.init()
pygame.display.set_caption("Battery Monitor")
screen = pygame.display.set_mode((win_width, win_height), 16)

# Set up SMBus
bus = smbus.SMBus(1)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

# Set up Tkinter popup
popup_closed = False

def check_power_loss():
    while True:
        i = GPIO.input(PLD_PIN)
        if i == 0:
            GPIO.output(BUZZER_PIN, 0)
        elif i == 1:
            print("Power Supply A/C Lost")
            GPIO.output(BUZZER_PIN, 1)
            time.sleep(0.1)
            GPIO.output(BUZZER_PIN, 0)
            time.sleep(0.1)
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

def display_data(voltage, capacity):
    # Set background color to white
    screen.fill((0, 0, 0))

    # Draw capacity bar on center of screen
    bar_x = (win_width - 80) // 2
    bar_y = (win_height - 360) // 2
    bar_w = 80
    bar_h = 360
    green = (55, 255, 55)
    purple = (255, 0, 255)

    # Draw purple rectangle at the top of the capacity graph
    pygame.draw.rect(screen, purple, (((win_width // 2) - 30), bar_y - 20, bar_w - 20, 20))

    # Draw capacity bar with purple border
    fill_h = int(float(capacity) / 100 * bar_h)
    fill_y = bar_y + bar_h - fill_h
    fill_rect = pygame.Rect(bar_x, fill_y, bar_w, fill_h)
    pygame.draw.rect(screen, purple, fill_rect, 3)
    pygame.draw.rect(screen, green, fill_rect.inflate(-6, -6))

    # Draw voltage on top of the battery
    font = pygame.font.Font(None, 36)
    text_voltage = font.render(f"{voltage:.2f}V", True, (255, 0, 255))
    voltage_x = (win_width - text_voltage.get_width()) // 2
    voltage_y = bar_y + 160
    screen.blit(text_voltage, (voltage_x, voltage_y))

    # Draw capacity as number percentage below the voltage number
    text_capacity = font.render(f"{int(capacity)}%", True, (255, 0, 255))
    capacity_x = (win_width - text_capacity.get_width()) // 2
    capacity_y = voltage_y + 36
    screen.blit(text_capacity, (capacity_x, capacity_y))

    # Update display
    pygame.display.update()

def close_popup():
    global popup_closed
    popup_closed = True
    popup.destroy()

def flash_reboot_led():
    for _ in range(20):  # Flash the reboot LED 10 times
        GPIO.output(reboot_led, GPIO.HIGH)
        time.sleep(0.25)
        GPIO.output(reboot_led, GPIO.LOW)
        time.sleep(0.25)

def button_callback(channel):
    button_press_time = time.time()
    while GPIO.input(power_btn) == GPIO.LOW:
        pass
    button_release_time = time.time()
    button_duration = button_release_time - button_press_time

    if 1 < button_duration < 3:
        print("Button pressed for {:.2f} seconds. Initiating system reboot...".format(button_duration))
        GPIO.output(power_led, GPIO.LOW)
        flash_reboot_led()  # Flash the reboot LED before rebooting
        time.sleep(10)  # Delay before initiating the reboot command
        GPIO.output(reboot_led, GPIO.LOW)  # Ensure the reboot LED is turned OFF
        os.system("sudo reboot")
    elif button_duration > 3:
        print("Button pressed for {:.2f} seconds. Initiating system shutdown...".format(button_duration))
        GPIO.output(power_led, GPIO.LOW)
        flash_reboot_led()  # Flash the reboot LED before rebooting
        time.sleep(10)  # Delay before initiating the reboot command
        GPIO.output(reboot_led, GPIO.LOW)  # Ensure the reboot LED is turned OFF
        os.system("sudo shutdown -h now")

# Remove any existing edge detection events and start threading
GPIO.remove_event_detect(power_btn)
# Add event detection on GPIO 16 falling edge
GPIO.add_event_detect(power_btn, GPIO.FALLING, callback=button_callback, bouncetime=200)

check_power_loss_thread = threading.Thread(target=check_power_loss)
check_power_loss_thread.start()

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Read data from SMBus
    voltage = readVoltage(bus)
    capacity = readCapacity(bus)

    # Display data on screen
    display_data(voltage, capacity)

    # Add delay
    pygame.time.delay(1000)
    
#     # Check battery status
#     if capacity >= 100:
#         if voltage >= 4.20:
#             popup = tk.Tk()
#             popup.title('Full Battery')
#             # create label widget
#             label = tk.Label(popup, text='Battery full!\nConsider unplugging\nyour batteries', padx=10, pady=10)
#             label.pack()
#             # create OK button widget
#             ok_button = tk.Button(popup, text='OK', command=close_popup)
#             ok_button.pack()
#             popup.wait_visibility()  # Wait for the window to become visible
#             popup.wait_window()  # Wait for the window to close
#             if popup_closed:
#                 continue

    if capacity < 20:
        if voltage < 3.52:
            popup = tk.Tk()
            popup.title('Shutdown Warning')
            # create label widget
            label = tk.Label(popup, text='Battery low!\nShutting down in 10 seconds!!!\nConsider plugging in\nyour batteries', padx=10, pady=10)
            label.pack()
            popup.wait_visibility()  # Wait for the window to become visible
            time.sleep(10)
            GPIO.output(GPIO_PORT, GPIO.HIGH)
            time.sleep(3)
            GPIO.output(GPIO_PORT, GPIO.LOW)
