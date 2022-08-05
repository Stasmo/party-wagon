import board
import digitalio
import time
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from analogio import AnalogIn
from pwmio import PWMOut

def get_voltage(pin):
  return (pin.value * 3.3) / 65536

class WagonController:

  def __init__(self):
    self.command_char         = '§'
    self.throttle_pin_number  = board.A1
    self.go_button_pin_number = board.D7
    self.speed_pin_number     = board.D9
    self.lpwm_pin_number      = board.D11
    self.rpwm_pin_number      = board.D12

    self.initialize_motor_controller()
    self.initialize_go_button()
    self.initialize_throttle()
    self.initialize_bluetooth()

  def initialize_bluetooth(self):
    BLERadio.name = "Party Wagon"
    self.ble = BLERadio()
    self.ble.name = "Party Wagon"
    self.uart = UARTService()
    self.advertisement = ProvideServicesAdvertisement(self.uart)
    self.ble.start_advertising(self.advertisement)

  def initialize_go_button(self):
    self.go_button = digitalio.DigitalInOut(self.go_button_pin_number)
    self.go_button.direction = digitalio.Direction.INPUT
    self.go_button.pull = digitalio.Pull.DOWN

  def initialize_throttle(self):
    self.throttle = AnalogIn(self.throttle_pin_number)
    self.throttle_speed = 0

  def initialize_motor_controller(self):
    self.speed_pin = PWMOut(self.speed_pin_number, frequency=15000, duty_cycle=0)

    self.lpwm = digitalio.DigitalInOut(self.lpwm_pin_number)
    self.rpwm = digitalio.DigitalInOut(self.rpwm_pin_number)
    self.lpwm.direction = digitalio.Direction.OUTPUT
    self.rpwm.direction = digitalio.Direction.OUTPUT
    self.lpwm.value = False
    self.rpwm.value = False

    self.direction = "stop"
    self.step = int(65535 / 10)
    self.set_speed(self.step * 5)

  def set_speed(self, speed):
    try:
      self.speed = int(speed)
      if (self.speed > 65535):
        self.speed = 65535
      if (self.speed < 0):
        self.speed = 0
      self.speed_pin.duty_cycle = self.speed
      self.uart.write(':spe:{}'.format(self.speed))
    except:
      print('Could not set speed to {}'.format(speed))

  def set_direction(self, direction):
    print('Setting direction: {}'.format(direction))
    if not (direction in ['f', 'b', 's']):
      direction = 's'
    self.direction = direction
    if direction == "f":
      self.lpwm.value = False
      self.rpwm.value = False
      self.lpwm.value = True
    elif direction == "b":
      self.rpwm.value = False
      self.lpwm.value = False
      self.rpwm.value = True
    elif direction == "s":
      self.rpwm.value = False
      self.lpwm.value = False
    self.uart.write('{}:dir:{}'.format(self.command_char, self.direction))

  def control(self):
    throttle_voltage = get_voltage(self.throttle)

    if not self.ble.connected:
      if not self.ble.advertising:
        self.ble.start_advertising(self.advertisement)
      if self.go_button.value and self.direction != "f":
        self.set_direction("f")
      elif not self.go_button.value and throttle_voltage < 1.0 and self.direction != "s":
        self.set_direction("s")
      if throttle_voltage > 1.0:
        if self.direction != "f":
          self.set_direction("f")
        self.throttle_speed = int(((throttle_voltage - 1.0) / 1.5) * 37000)
        print('Throttle speed: {}'.format(100 * self.throttle_speed / 65535))
      else:
        self.throttle_speed = 0

    # Now we're connected

    if self.ble.connected:
      if self.uart.in_waiting:
        message = self.uart.readline().decode()

        if message.startswith(self.command_char):
          parts = message.split(':')
          if parts[1] == 'dir':
            self.set_direction(parts[2])
          elif parts[1] == 'spe':
            self.set_speed(int(parts[2]))

        print('Message: {}'.format(message))

    if self.throttle_speed > 0:
      self.speed_pin.duty_cycle = self.throttle_speed
    else:
      self.speed_pin.duty_cycle = self.speed

    time.sleep(0.05)

wagon_controller = WagonController()

while True:
  wagon_controller.control()