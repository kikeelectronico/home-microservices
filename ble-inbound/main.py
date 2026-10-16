from bluepy import btle
import time
import json
import logging

from mqtt import set_mqtt_client
from constants import (
  API_RX_CHARACTERISTIC_UUID,
  API_SERVICE_UUID,
  API_TX_CHARACTERISTIC_UUID,
  ONLINE_TIMEOUT
)
from homeware import Homeware
from settings import Settings
from shutdown import register_shutdown_handlers, stop_requested, wait_for_stop

# Declare vars
ble_link = None
rx_char = None
last_update = {}
settings = None
mqtt_client = None
homeware = None
BLE_SENSORS = None
BLE_PRESENCE = None

# Callback for BLE sensors
class MyDelegate(btle.DefaultDelegate):
    def __init__(self, device_id):
        self.device_id = device_id
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        data = bytearray(data)
        if data[0] == 1:
            if len(data) == 5:
                # Update battery
                homeware.execute(self.device_id,"capacityRemaining",[{"rawValue": data[1], "unit":"PERCENTAGE"}])
                if data[1] == 100: homeware.execute(self.device_id,"descriptiveCapacityRemaining","FULL")
                elif data[1] >= 70: homeware.execute(self.device_id,"descriptiveCapacityRemaining","HIGH")
                elif data[1] >= 40: homeware.execute(self.device_id,"descriptiveCapacityRemaining","MEDIUM")
                elif data[1] >= 10: homeware.execute(self.device_id,"descriptiveCapacityRemaining","LOW")
                else: homeware.execute(self.device_id,"descriptiveCapacityRemaining","CRITICALLY_LOW")

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
                  homeware.execute(self.device_id,"thermostatTemperatureAmbient",temp)
                  homeware.execute(self.device_id,"thermostatHumidityAmbient",hum)
                elif "temperature" in self.device_id:
                  homeware.execute(self.device_id,"temperatureAmbientCelsius",temp)
                  homeware.execute(self.device_id,"humidityAmbientPercent",hum)
                homeware.execute(self.device_id,"online",True)
            else:
                logging.warning("Unknown package from " + self.device_id)
        elif data[0] == 7:
            logging.warning("Low battery: " + self.device_id)
            homeware.execute(self.device_id,"descriptiveCapacityRemaining","LOW")
            homeware.execute(self.device_id,"online",False)

# BLE sensors
def getSensors():
   for device in BLE_SENSORS:
      try:
        print("connecting", device)
        # Connect to device
        logging.info("Connecting to: " + device)
        ble_link = btle.Peripheral(BLE_SENSORS[device]["mac"], btle.ADDR_TYPE_RANDOM)
        ble_link.withDelegate(MyDelegate(device))
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
        last_update[device] = time.time()
      except btle.BTLEDisconnectError:
        logging.warning("Device unreachable: " + device)
        if device in last_update:
          if time.time() - last_update[device] > ONLINE_TIMEOUT:
            if homeware.get(device, "online"):
              mqtt_client.publish("notificacion/text/alert", device + " inaccesible")
            logging.warning("Device offline: " + device)
            homeware.execute(device,"online",False)

# BLE presence
def verifyPresence():
  scanner = btle.Scanner()
  dispositivos = scanner.scan(10.0)
  macs = [dev.addr.upper() for dev in dispositivos]
  names = [dev.getValueText(0x09) for dev in dispositivos]
  for device in BLE_PRESENCE:
      if not homeware.get(device["id"], "enable") == (device["name"] in names):
        homeware.execute(device["id"],"enable", device["name"] in names)


# Main entry point
def main():
  global settings
  global BLE_SENSORS
  global BLE_PRESENCE
  global mqtt_client
  global homeware
  # Register shutdown handlers
  register_shutdown_handlers()

  # Load settings
  settings = Settings()
  settings.load_settings()

  logging.basicConfig(
    level=logging.INFO,
    format=(
      "%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
      if settings.env == "dev"
      else "%(message)s"
    )
  )
  BLE_SENSORS = json.loads(settings.ble_sensors)
  BLE_PRESENCE = json.loads(settings.ble_presence)

  # Instantiate objects
  mqtt_client = set_mqtt_client(
    settings.mqtt_host_network,
    settings.mqtt_port,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id
  )
  homeware = Homeware(mqtt_client, settings.homeware_api_url_network, settings.homeware_api_key)
  
  mqtt_client.loop_start()
  logging.info("Starting " + settings.service_id)

  while not stop_requested():
    getSensors()
    if stop_requested():
      break
    verifyPresence()
    wait_for_stop(1)

  logging.info("Disconnecting from the MQTT broker.")
  mqtt_client.loop_stop()
  mqtt_client.disconnect()
  logging.info("Shutdown completed.")

if __name__ == "__main__":
  main()
