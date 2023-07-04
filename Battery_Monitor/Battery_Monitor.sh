#!/bin/bash

DISPLAY=:0 nohup python3 /home/pi/battery_monitor/Battery_Monitor.py >/dev/null 2>&1 &
