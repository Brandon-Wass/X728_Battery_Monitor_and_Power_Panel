#!/bin/bash

DISPLAY=:0 nohup python3 $(find / -name "Battery_Monitor.py" 2>/dev/null) >/dev/null 2>&1 &
