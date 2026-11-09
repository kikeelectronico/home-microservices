import json
import time

from constants import HEARTBEAT_TOPIC, TASK_ACK_TOPIC


class TaskSchedulerService:

  def __init__(self):
    self.tasks = []
    self.homeware = None
    self.mqtt_client = None

  def initialize(self, homeware, mqtt_client):
    self.homeware = homeware
    self.mqtt_client = mqtt_client

  def _handle_message(self, topic, payload):
    if topic == HEARTBEAT_TOPIC:
      self._process_due_tasks()
      return

    new_task = json.loads(payload)
    if new_task["action"] == "set":
      if "delta" in new_task:
        new_task["time"] = time.time() + new_task["delta"]
      self.tasks.append(new_task)
      self.mqtt_client.publish(TASK_ACK_TOPIC, json.dumps(new_task))
    elif new_task["action"] == "delete":
      for index, task in enumerate(self.tasks):
        if task["id"] == new_task["id"]:
          del self.tasks[index]
          self.mqtt_client.publish(TASK_ACK_TOPIC, json.dumps(new_task))

  def _process_due_tasks(self):
    for index, task in enumerate(self.tasks):
      if task["time"] < time.time():
        assert_pass = True
        for condition in task["asserts"]:
          if not self.homeware.get(condition["device_id"], condition["param"]) == condition["value"]:
            assert_pass = False
            break
        if assert_pass:
          self.homeware.execute(
            task["target"]["device_id"],
            task["target"]["param"],
            task["target"]["value"]
          )
        del self.tasks[index]
