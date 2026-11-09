import time


def process(homeware, tasks):
  # Process pending tasks
  for task_id in list(tasks.keys()):
    task = tasks[task_id]
    if (time.time() - task["time"]) > 10:
      homeware.execute(task["device_id"], task["param"], task["value"])
      del tasks[task_id]
