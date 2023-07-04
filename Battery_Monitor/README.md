# Battery_Monitor

This Python script reads the voltage and battery capacity from an I2C-connected battery monitoring IC and displays them on a Pygame window.
It also checks the battery status and displays a warning popup if the battery is full or low.

The script uses the smbus and struct modules to communicate with the I2C device
and the RPi.GPIO module to control a GPIO pin that triggers a shutdown when the battery level is critically low.

The Pygame window is created with a purple capacity graph on the left side and the voltage and capacity displayed in numbers on the right side.
The capacity bar fills up according to the battery level percentage, and the voltage is displayed on top of the battery graphic.
If the battery is full, a popup window is displayed with a message to unplug the batteries.
If the battery is low, a popup window is displayed with a message to plug in the batteries and a countdown timer for a forced shutdown.

The script runs in an infinite loop and updates the display every second. The loop also listens for Pygame events,
such as the window close event, and triggers the appropriate actions. The main loop is interruptable by closing the Pygame window.

----------------------------

This code is based on the Geekworm X728 V2.3.
and meant to be used on Raspberry Pi SBCs that are compatible with the Geekworm X728 UPS units.

CPU usage is negligably low, running near 0%-2%, on a Raspberry Pi 4B.

Dialog windows do pause the program until closed, which is effectievly helpful in "Full Battery" situations.
Dialog window will reopen when closed if the battery capacity is 100% or above AND battery voltage is 4.20 volts or above.
This stipulation has been tested when the system is plugged in to a power supply versus running without a power supply connected to the X728 board.

The low battery "Shutdown" event window is not closable,
as an event has been triggered to shutdown the system simultaneously to the "Shutdown" popup being triggered.


----------------------


Credit to Geekworm for supplying the code to get reads on voltage and capacity.
