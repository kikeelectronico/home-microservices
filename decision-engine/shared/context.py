from typing import Any, Dict
import json
import requests
import logging

class Context:

    __mqtt_client = None
    __url = "localhost"
    __token = "token"

    def __init__(self, mqtt_client, host, token) -> None:
        self.__mqtt_client = mqtt_client
        self.__url = host
        self.__token = token

        fail = False
        if self.__url == "no_set":
            logging.error("HOMEWARE_API_URL env var isn't set")
            fail = True
        if self.__token == "no_set":
            logging.error("HOMEWARE_API_KEY env var isn't set")
            fail = True
        if fail:
            exit()

    def get(self, id: str, param: str) -> Any:
        try:
            url = self.__url + "/api/devices/" + id + "/states/" + param
            headers = {"Authorization": "bearer " + self.__token}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            logging.warning("Fail to get Homeware status. Status code: %s", response.status_code)
            return {}
        except (requests.ConnectionError, requests.Timeout) as exception:
            logging.warning("Fail to get Homeware status. Conection error.")
            return {}

    def getDevice(self, id: str) -> Any:
        try:
            url = self.__url + "/api/devices/" + id
            headers = {"Authorization": "bearer " + self.__token}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            logging.warning("Fail to get Homeware status. Status code: %s", response.status_code)
            return {}
        except (requests.ConnectionError, requests.Timeout) as exception:
            logging.warning("Fail to get Homeware device. Conection error.")
            return {}