import paho.mqtt.client
import json

class Logger:
    
    __mqtt_client = None
    __service = "Unknown"

    def __init__(self, mqtt_client = None, service = "Unknown"):
        if type(mqtt_client) == paho.mqtt.client.Client:
            self.__mqtt_client = mqtt_client
        if type(service) == str:
            self.__service = service

    def log(self, message, severity = "INFO"):
        if self.__mqtt_client is not None:
            payload = {
                "service": self.__service,
                "severity": severity,
                "message": message
            }
            self.__mqtt_client.publish("log", json.dumps(payload))
        else:
            print("No connection to mqtt broker")