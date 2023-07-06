#!/bin/bash

DISPLAY=:0 nohup python3 $(find / -name "System_Reboot.py" 2>/dev/null) >/dev/null 2>&1 &
