import time


class MonitorResponseService:

  def __init__(self, settings, bigquery_client):
    self.settings = settings
    self.bigquery_client = bigquery_client
    self.pending_measurement = None

  def _handle_message(self, topic, payload):
    now = time.perf_counter()

    if topic == self.settings.response_test_trigger_topic:
      self.pending_measurement = now
      return

    if topic == self.settings.response_test_response_topic:
      if self.pending_measurement is None:
        return

      elapsed = now - self.pending_measurement
      elapsed_ms = int(elapsed * 1000)
      self.pending_measurement = None
      timestamp = int(time.time())
      query_job = self.bigquery_client.query(
        """
          INSERT INTO {}
          (time, trigger, response, duration)
          VALUES ({},"{}","{}",{});
        """.format(
          self.settings.response_ddbb,
          timestamp,
          self.settings.response_test_trigger_topic,
          self.settings.response_test_response_topic,
          elapsed_ms
        )
      )
      query_job.result()
