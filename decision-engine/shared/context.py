from typing import Any, Dict
import json
import requests
import logging

REQUEST_TIMEOUT = 10

class Context:

    __mqtt_client = None
    __url = "localhost"
    __token = "token"

    def __init__(self, mqtt_client, host, token) -> None:
        self.__mqtt_client = mqtt_client
        self.__url = host
        self.__token = token

    def get(self, id: str, param: str) -> Any:
        try:
            url = self.__url + "/api/devices/" + id + "/states/" + param
            headers = {"Authorization": "bearer " + self.__token}
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                return response.json()
            logging.warning("Fail to get Homeware status. Status code: %s", response.status_code)
            return None
        except (requests.ConnectionError, requests.Timeout) as exception:
            logging.warning("Fail to get Homeware status. Conection error.")
            return None

    def getDevice(self, id: str) -> Any:
        try:
            url = self.__url + "/api/devices/" + id
            headers = {"Authorization": "bearer " + self.__token}
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                return response.json()
            logging.warning("Fail to get Homeware status. Status code: %s", response.status_code)
            return {}
        except (requests.ConnectionError, requests.Timeout) as exception:
            logging.warning("Fail to get Homeware device. Connection error.")
            return {}
