# Power_Panel_with_X728_Integration

--------------------------

There are two versions of this program.

The regular program disables video output so it can perform as a system service.

The GUI version combines the functionality of this program with the Battey Monitor program.

------------------------

Clone this git or download and extract the files from the zip.

Once you have the files on your system, open a terminal in the folder containing the files.

Run the following command "sudo bash pwr_board.sh"

This will create, install, and start a background service of this program for you.

If you want to remove the service, type the following comands:

sudo systemctl stop pwr_board.service

sudo rm /etc/systemd/system/pwr_board.service

----------------------------

This Python script uses the RPi.GPIO library to configure and interact with GPIO pins on a Raspberry Pi. The script includes functions to check for power loss, handle button press events, and perform system reboot and shutdown actions.


To summarize the functionality of the script:


Import necessary modules and libraries, including RPi.GPIO, os, time, and threading.

Set up GPIO mode and pin assignments for various components.

Define a function, check_power_loss(), that continuously checks the status of a power loss detection pin (PLD_PIN).

If the pin is low (0), it indicates power supply loss, and the buzzer pin (BUZZER_PIN) is set to low (0). The buzzer pin is briefly pulsed to create an audible beep.

If the pin is high (1), it indicates power supply is connected.

Define a function, flash_reboot_led(), to rapidly toggle the reboot LED state for visual feedback before system reboot or shutdown.

Define a callback function, button_callback(), to handle button press events on the power button (power_btn).

Calculate the duration of button press by measuring the time between button press and release.

If the button is pressed for between 1 and 3 seconds, initiate a system reboot.

If the button is pressed for more than 3 seconds, initiate a system shutdown.

Set up event detection for the power button using GPIO.add_event_detect() and assign the button_callback() function as the callback.

Create a separate thread, check_power_loss_thread, to continuously run the check_power_loss() function.

Start the thread.

Handle Keyboard Interrupt (KeyboardInterrupt) to gracefully stop the script when interrupted.

Clean up GPIO settings and exit the script.

Please note that this script assumes the proper setup of the hardware components and is designed to be run on a Raspberry Pi.


----------------------


The intention of this code is to run the file as a service.

I do have a stripped down version of the Battery Monitor program that pairs well with this service, giving you the service in the background and a visual indicator of battery capacity and voltage.

The bash script pwr_board.sh does this automatically.

This script features code to pulse a GPIO connected LED if a reboot or shutdown is triggered, and it sets off the buzzer on the X728 board if the A/C power adapter is disconnected.

This makes the script handy if power loss occurs.

You can disable the entire buzzer section if you intend to go mobile, but don't forget to disable the threading for it as well.

This code is based on the Geekworm X728 V2.3. and meant to be used on Raspberry Pi SBCs that are compatible with the Geekworm X728 UPS units.

CPU usage is negligably low, running near 0%-2%, on a Raspberry Pi 4B.


----------------------


Credit to Geekworm for supplying the code for getting reads on voltage, capacity, and accessing the fancy buzzer.
