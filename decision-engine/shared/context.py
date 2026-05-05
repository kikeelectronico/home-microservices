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

    def get(self, id: str, param: str) -> Any:
        if self.__token == "no_set" or self.__url == "no_set":
            self._fail_to_update = True
            logging.error("Homeware env vars aren't set")
        else:
            try:
                if param == "all":
                    url = self.__url + "/api/devices/" + id + "/states"
                else:
                    url = self.__url + "/api/devices/" + id + "/states/" + param
                headers = {"Authorization": "bearer " + self.__token}
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json()
                else:
                    logging.warning("Fail to get Homeware status. Status code: " + str(response.status_code))
                    return (False, {})
            except (requests.ConnectionError, requests.Timeout) as exception:
                logging.warning("Fail to get Homeware status. Conection error.")
                self._fail_to_update = False
