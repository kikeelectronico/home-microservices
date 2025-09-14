import paho.mqtt.client as mqtt
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from asyncio import sleep
import time
import logging

from spotify import Spotify
from water import Water
from weather import Weather
from homeware import Homeware
from internet import Internet

# Load env vars
if os.environ.get("ENV", "dev") == "dev":
  from dotenv import load_dotenv
  load_dotenv(dotenv_path="../.env")

MQTT_USER = os.environ.get("MQTT_USER", "no_set")
MQTT_PASS = os.environ.get("MQTT_PASS", "no_set")
MQTT_HOST = os.environ.get("MQTT_HOST", "no_set")
MQTT_PORT = 1883
ENV = os.environ.get("ENV", "dev")

# Define constants
SERVICE = "data-panel-api-" + ENV

# Instantiate objects
app = FastAPI()
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=SERVICE) 

# Check env vars
def report(message):
  print(message)
  exit()
if MQTT_USER == "no_set":
  report("MQTT_USER env vars no set")
if MQTT_PASS == "no_set":
  report("MQTT_PASS env vars no set")
if MQTT_HOST == "no_set":
  report("MQTT_HOST env vars no set")

 # Connect to the mqtt broker
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
logging.info("Starting " + SERVICE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

spotify = Spotify()
water = Water()
weatherapi = Weather()
homeware = Homeware()
internet = Internet()

@app.get("/")
async def root():
  return {"message": "Hello, World!"}

async def streamEvents():
  last = {}
  while True:
    # Internet
    connected = internet.checkConnectivity()
    if not last.get("connected", False) == connected:
      event = {
        "type": "internet",
        "data": {
          "connected": connected
        }
      }
      last["connected"] = connected
      yield f"data: {json.dumps(event)}\n\n"
      await sleep(0.1)
    # Spotify
    playing = spotify.getPlaying(max_tries=2)
    if not last.get("playing", {}) == playing:
      event = {
        "type": "spotify",
        "data": {
          "playing": playing
        }
      }
      last["playing"] = playing
      yield f"data: {json.dumps(event)}\n\n"
      await sleep(0.1)
    # Home
    (status_flag, home_status) = homeware.getStatus()
    if not last.get("home_status", {}) == home_status:
      event = {
        "type": "home",
        "data": {
          "status": home_status
        },
        "flags": {
          "status": status_flag
        }
      }
      last["home_status"] = home_status
      yield f"data: {json.dumps(event)}\n\n"
      await sleep(0.1)
     # Water
    water_data = water.getWater()
    if not last.get("water_data", {}) == water_data:
      event = {
        "type": "water",
        "data": {
          "water": water_data,
        },
        "flags": {}
      }
      last["water_data"] = water_data
      yield f"data: {json.dumps(event)}\n\n"
      await sleep(0.1)
    # Weather
    (fail_to_update, current_flag, current, forecast_flag, forecast, alerts_flag, alerts) = weatherapi.getWeather()
    if not last.get("forecast", {}) == forecast:
      event = {
        "type": "weather",
        "data": {
          "current": current,
          "forecast": forecast,
          "alerts": alerts
        },
        "flags": {
          "current": current_flag,
          "forecast": forecast_flag,
          "alerts": alerts_flag
        }
      }
      last["forecast"] = forecast
      yield f"data: {json.dumps(event)}\n\n"
      await sleep(0.1)
    if time.time() - last.get("ping", 0) > 5:
      event = {
        "type": "ping",
        "data": {},
        "flags": {}
      }
      last["ping"] = time.time()
      yield f"data: {json.dumps(event)}\n\n"
      await sleep(0.1)

@app.get("/stream")
async def stream():
  return StreamingResponse(streamEvents(), media_type="text/event-stream")

if __name__ == "__main__":
   import uvicorn
   uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )