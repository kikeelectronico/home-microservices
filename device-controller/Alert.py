
class Alert:

  __mqtt_client = None

  def __init__(self, mqtt_client):
    self.__mqtt_client = mqtt_client

  # Send a voice alert
  def voice(self, input_text, speaker=""):
    output_text = input_text
    # Send the message
    self.__mqtt_client.publish("voice-alert/speakers", speaker)
    self.__mqtt_client.publish("voice-alert/text", output_text)

  # Send a message alert
  def message(self, text):
    self.__mqtt_client.publish("message-alerts", text)