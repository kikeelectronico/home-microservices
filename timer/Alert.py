
class Alert:

  __mqtt_client = None

  def __init__(self, mqtt_client):
    self.__mqtt_client = mqtt_client

  # Send a voice alert
  def voice(self, input_text):
    output_text = input_text
    # Send the message
    self.__mqtt_client.publish("notificacion/voice/alert", output_text)

  # Send a message alert
  def message(self, text):
    self.__mqtt_client.publish("notificacion/text/alert", text)