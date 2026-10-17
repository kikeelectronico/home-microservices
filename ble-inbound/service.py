import logging
import time

from bluepy import btle

from constants import (
  API_RX_CHARACTERISTIC_UUID,
  API_SERVICE_UUID,
  API_TX_CHARACTERISTIC_UUID,
  ONLINE_TIMEOUT
)
from shutdown import stop_requested, wait_for_stop


class BLEInboundService:

  def __init__(self):
    self.homeware = None
    self.mqtt_client = None
    self.ble_sensors = None
    self.ble_presence = None
    self.last_update = {}

  def initialize(self, homeware, mqtt_client, ble_sensors, ble_presence):
    self.homeware = homeware
    self.mqtt_client = mqtt_client
    self.ble_sensors = ble_sensors
    self.ble_presence = ble_presence

  # BLE sensors
  def _get_sensors(self):
    for device in self.ble_sensors:
      ble_link = None
      try:
        print("connecting", device)
        # Connect to device
        logging.info("Connecting to: " + device)
        ble_link = btle.Peripheral(self.ble_sensors[device]["mac"], btle.ADDR_TYPE_RANDOM)
        ble_link.withDelegate(BLEDelegate(self.homeware, device))
        # Get the API service
        service_uuid = btle.UUID(API_SERVICE_UUID)
        ble_service = ble_link.getServiceByUUID(service_uuid)
        # Set the notifications
        tx_uuid = btle.UUID(API_TX_CHARACTERISTIC_UUID)
        tx_char = ble_service.getCharacteristics(tx_uuid)[0]
        setup_data = b"\x01\x00"
        cHandle = tx_char.valHandle
        ble_link.writeCharacteristic(cHandle + 1, setup_data)
        # Get the API RX characteristic
        rx_uuid = btle.UUID(API_RX_CHARACTERISTIC_UUID)
        rx_char = ble_service.getCharacteristics(rx_uuid)[0]
        # Request temperature and humidity
        rx_char.write(bytes.fromhex("570f31"))
        ble_link.waitForNotifications(5)
        # Request device info
        rx_char.write(bytes.fromhex("570200"))
        ble_link.waitForNotifications(5)
        # Disconnect
        ble_link.disconnect()
        ble_link = None
        # Update timestamp
        self.last_update[device] = time.time()
      except btle.BTLEDisconnectError:
        logging.warning("Device unreachable: " + device)
        if device in self.last_update:
          if time.time() - self.last_update[device] > ONLINE_TIMEOUT:
            if self.homeware.get(device, "online"):
              self.mqtt_client.publish("notificacion/text/alert", device + " inaccesible")
            logging.warning("Device offline: " + device)
            self.homeware.execute(device,"online",False)
      finally:
        if ble_link is not None:
          try:
            ble_link.disconnect()
          except Exception as exc:
            logging.warning("Fail to disconnect from BLE device %s: %s", device, exc)

  # BLE presence
  def _verify_presence(self):
    scanner = btle.Scanner()
    dispositivos = scanner.scan(10.0)
    names = [dev.getValueText(0x09) for dev in dispositivos]
    for device in self.ble_presence:
      if not self.homeware.get(device["id"], "enable") == (device["name"] in names):
        self.homeware.execute(device["id"],"enable", device["name"] in names)

  def run(self):
    while not stop_requested():
      self._get_sensors()
      if stop_requested():
        break
      self._verify_presence()
      wait_for_stop(1)


class BLEDelegate(btle.DefaultDelegate):

  def __init__(self, homeware, device_id):
    self.homeware = homeware
    self.device_id = device_id
    btle.DefaultDelegate.__init__(self)

  def handleNotification(self, cHandle, data):
    data = bytearray(data)
    if data[0] == 1:
      if len(data) == 5:
        # Update battery
        self.homeware.execute(self.device_id,"capacityRemaining",[{"rawValue": data[1], "unit":"PERCENTAGE"}])
        if data[1] == 100: self.homeware.execute(self.device_id,"descriptiveCapacityRemaining","FULL")
        elif data[1] >= 70: self.homeware.execute(self.device_id,"descriptiveCapacityRemaining","HIGH")
        elif data[1] >= 40: self.homeware.execute(self.device_id,"descriptiveCapacityRemaining","MEDIUM")
        elif data[1] >= 10: self.homeware.execute(self.device_id,"descriptiveCapacityRemaining","LOW")
        else: self.homeware.execute(self.device_id,"descriptiveCapacityRemaining","CRITICALLY_LOW")

        if data[1] < 5:
          logging.error(self.device_id + ": batería muy baja")
        elif data[1] < 10:
          logging.warning(self.device_id + ": batería baja")

      elif len(data) == 4:
        # Update temperature and humidity
        temp_int = (data[2] - 128) if data[2] >= 128 else (data[2] * -1)
        temp_dec = data[1] if data[1] < 16 else 0
        temp = temp_int + (temp_dec/10)
        hum = data[3] if data[3] < 128 else (data[3] - 128)
        if "thermostat" in self.device_id:
          self.homeware.execute(self.device_id,"thermostatTemperatureAmbient",temp)
          self.homeware.execute(self.device_id,"thermostatHumidityAmbient",hum)
        elif "temperature" in self.device_id:
          self.homeware.execute(self.device_id,"temperatureAmbientCelsius",temp)
          self.homeware.execute(self.device_id,"humidityAmbientPercent",hum)
        self.homeware.execute(self.device_id,"online",True)
      else:
        logging.warning("Unknown package from " + self.device_id)
    elif data[0] == 7:
      logging.warning("Low battery: " + self.device_id)
      self.homeware.execute(self.device_id,"descriptiveCapacityRemaining","LOW")
      self.homeware.execute(self.device_id,"online",False)
