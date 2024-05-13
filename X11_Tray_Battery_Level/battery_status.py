import sys
import struct
import smbus
import time
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

# Setup I2C bus
bus = smbus.SMBus(1)

def read_voltage(bus):
    address = 0x36
    try:
        read = bus.read_word_data(address, 2)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        voltage = swapped * 1.25 / 1000 / 16
        return voltage
    except Exception as e:
        print(f"Error reading voltage: {e}")
        return 0.0

def read_capacity(bus):
    address = 0x36
    try:
        read = bus.read_word_data(address, 4)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        capacity = swapped / 256
        return capacity
    except Exception as e:
        print(f"Error reading capacity: {e}")
        return 0

def update_battery_status(tray_icon):
    voltage = read_voltage(bus)
    capacity = read_capacity(bus)
    tray_icon.setToolTip(f"Battery Monitoring App\nVoltage: {voltage:.2f}V\nCapacity: {capacity}%")

def create_tray_icon(app):
    tray_icon = QSystemTrayIcon(QIcon("battery_icon.png"), app)
    update_battery_status(tray_icon)  # Initial tooltip update

    menu = QMenu()
    exit_action = QAction("Exit", app)
    exit_action.triggered.connect(app.quit)
    menu.addAction(exit_action)

    tray_icon.setContextMenu(menu)
    tray_icon.show()

    global timer  # Ensure the timer is kept in scope
    timer = QTimer()
    timer.timeout.connect(lambda: update_battery_status(tray_icon))
    timer.start(5000)

    return tray_icon

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tray_icon = create_tray_icon(app)
    sys.exit(app.exec_())
