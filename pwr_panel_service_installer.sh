#!/bin/bash

# Set the desired verbosity level (0 - minimal, 1 - moderate, 2 - high)
verbosity_level=0

# Adjust the verbosity level
if [[ "$verbosity_level" -eq 0 ]]; then
    set +x  # Disable verbose output
elif [[ "$verbosity_level" -eq 2 ]]; then
    set -x  # Enable high verbosity
else
    set -v  # Enable moderate verbosity
fi

# Variables
service_name="pwr_panel"
service_file="/etc/systemd/system/$service_name.service"
service_script=$(find / -name "pwr_panel.py" 2>/dev/null)
echo "The pwr_control.py file was found."
if [[ -z "$service_script" ]]; then
    echo "Failed to find pwr_panel.py file for $service_name"
    exit 1
fi

# Create the service file
cat <<EOF > $service_file
[Unit]
Description=Power board controller
After=network.target

[Service]
ExecStart=$service_script

[Install]
WantedBy=default.target
EOF
echo "The pwr_board.service file has been created"
# Reload systemd configuration
sudo systemctl daemon-reload
sleep 2
echo "Daemon reloaded"

# Enable and start the service
sudo systemctl enable $service_name
sleep 2
echo "Service enabled"

sudo systemctl start $service_name
sleep 2
echo "Service started. You can check the status with 'sudo systemctl status $service_name'"
