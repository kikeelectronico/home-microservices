from bluepy import btle
import paho.mqtt.client as mqtt
import os
import time
import json
import logging

from homeware import Homeware

if os.environ.get("MQTT_PASS", "no_set") == "no_set":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST_NETWORK", "no_set")
HOMEWARE_API_URL = os.environ.get("HOMEWARE_API_URL_NETWORK", "no_set")
HOMEWARE_API_KEY = os.environ.get("HOMEWARE_API_KEY", "no_set")
BLE_SENSORS = os.environ.get("BLE_SENSORS", "no_set")
BLE_PRESENCE = os.environ.get("BLE_PRESENCE", "no_set")
ENV = os.environ.get("ENV", "dev")

# Define constants
MQTT_PORT = 1883
SERVICE = "ble-inbound-" + ENV
ONLINE_TIMEOUT = 300
# API UUIDs
API_SERVICE_UUID ="cba20d00-224d-11e6-9fb8-0002a5d5c51b"
API_TX_CHARACTERISTIC_UUID= "cba20003-224d-11e6-9fb8-0002a5d5c51b"
API_RX_CHARACTERISTIC_UUID= "cba20002-224d-11e6-9fb8-0002a5d5c51b"

# Declare vars
ble_link = None
rx_char = None
last_update = {}

# Instantiate objects
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=SERVICE)
homeware = Homeware(mqtt_client, HOMEWARE_API_URL, HOMEWARE_API_KEY)

# Callback for BLE sensots
class MyDelegate(btle.DefaultDelegate):
    def __init__(self, device_id):
        self.device_id = device_id
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        data = bytearray(data)
        if data[0] == 1:
            if len(data) == 5:
                # Update batery
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
        # Get API RX the characteristic
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
if __name__ == "__main__":
  # Check env vars
  def report(message):
    print(message)
    exit()
  if MQTT_USER == "no_set": report("MQTT_USER env vars no set")
  if MQTT_PASS == "no_set": report("MQTT_PASS env vars no set")
  if MQTT_HOST == "no_set": report("MQTT_HOST env vars no set")
  if HOMEWARE_API_URL == "no_set": report("HOMEWARE_API_URL env vars no set")
  if HOMEWARE_API_KEY == "no_set": report("HOMEWARE_API_KEY env vars no set")
  if BLE_SENSORS == "no_set": report("BLE_SENSORS env vars no set")
  else: BLE_SENSORS = json.loads(BLE_SENSORS)
  if BLE_PRESENCE == "no_set": report("BLE_PRESENCE env vars no set")
  else: BLE_PRESENCE = json.loads(BLE_PRESENCE)
  
  # Connect to the mqtt broker
  mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
  mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
  logging.info("Starting " + SERVICE)

  while True:
    getSensors()
    verifyPresence()
    time.sleep(1)