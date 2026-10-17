import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from constants import DEVICE_IDS, TOPICS
from mqtt import set_mqtt_client
from service import DataPanelService
from settings import Settings
from shutdown import request_stop

# from spotify import Spotify

service = DataPanelService(DEVICE_IDS)


@asynccontextmanager
async def lifespan(app):
  settings = Settings()
  settings.load_settings()

  mqtt_client = set_mqtt_client(
    settings.mqtt_host,
    settings.mqtt_port,
    settings.mqtt_user,
    settings.mqtt_pass,
    settings.service_id,
    subscriptions=TOPICS,
    message_handler=service._handle_message
  )
  service.initialize(mqtt_client)
  mqtt_events_task = asyncio.create_task(service.dispatch_mqtt_events())
  try:
    mqtt_client.loop_start()
    logging.info("Starting " + settings.service_id)
    yield
  finally:
    request_stop()
    mqtt_client.disconnect()
    mqtt_client.loop_stop()
    mqtt_events_task.cancel()
    try:
      await mqtt_events_task
    except asyncio.CancelledError:
      pass


app = FastAPI(lifespan=lifespan)

app.add_middleware(
  CORSMiddleware,
  allow_origins=['*'],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# spotify = Spotify()

@app.get("/")
async def root():
  return {"message": "Hello, World!"}


@app.get("/stream")
async def stream():
  queue = service.add_sse_queue()
  service.request_initial_data()

  async def stream_with_cleanup():
    try:
      async for event in service.stream_events(queue):
        yield event
    finally:
      service.remove_sse_queue(queue)

  return StreamingResponse(stream_with_cleanup(), media_type="text/event-stream")


if __name__ == "__main__":
  import uvicorn
  uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=8000,
    reload=True,
  )
