#!/usr/bin/env python

import struct
import smbus
import sys
import time
import RPi.GPIO as GPIO
import pygame
import os
import tkinter as tk


# Driver modifiers
os.environ["SDL_AUDIODRIVER"] = "dummy"

# Initialize Pygame
pygame.init()

# Set display dimensions and icons
win_width = 100
win_height = 390

pygame.display.set_caption("Battery Monitor")

screen = pygame.display.set_mode((win_width, win_height), 16)

# Global settings
I2C_ADDR = 0x36

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

bus = smbus.SMBus(1) # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

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