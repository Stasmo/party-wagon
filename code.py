import board
import busio
import math
import neopixel
import time
import storage
import json

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

class MotorController:

  BLERadio.name = "Motor Controller"
  ble = BLERadio()
  ble.name = "Motor Controller"
  bleuart = UARTService()

  bleuart_advertisement = ProvideServicesAdvertisement(bleuart)

  ble.start_advertising(bleuart_advertisement)

  FRAMES_PER_SECOND = 60
  SECONDS_PER_FRAME = 1 / FRAMES_PER_SECOND
  LAST_FRAME = time.monotonic()

  procedure = ""
  procedure_save_file_name = "motor_control_loop.txt"

  def __init__(self):
    self.read_procedure()

  def read_procedure(self):
    try:
      with open(self.procedure_save_file_name, "r") as fp:
        self.procedure = fp.read()
    except Exception as e:
      print(e)
      print('Could not read motor control procedure.')

  def handle_ble(self):
    if not self.ble.connected:
      if not self.ble.advertising:
        self.ble.start_advertising(self.bleuart_advertisement)
      pass
    else:
      if self.bleuart.in_waiting:
        print("Receiving new ble.")
        s = self.bleuart.readline()
        data = s.decode()
        if data == "#### START PROCEDURE ####":
          print("Starting new procedure.")
          self.procedure = ""
        elif data == "#### END PROCEDURE ####":
          print("Saving procedure.")
          self.save_procedure()
          self.motor_control_loop = eval(self.procedure)
        else:
          print("Adding to procedure.")
          self.procedure += data

  def motor_control_loop(self):
    print("Waiting for motor control procedure.")
    time.sleep(0.5)

  def process(self):
    self.handle_ble()
    self.motor_control_loop()

  def save_procedure(self):
    try:
      storage.remount("/", False)
      with open(self.procedure_save_file_name, "w+") as fp:
        fp.write(self.procedure)
    except Exception as e:
      print(e)
      print("Could not write to disk")
    finally:
      storage.remount("/", True)

motor_controller = MotorController()

while True:
  motor_controller.process()

  print("Waiting for motor control procedure.")
  time.sleep(0.5)