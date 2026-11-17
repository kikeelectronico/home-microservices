class NotificationMessageService:

  def __init__(self, bot, chat_id):
    self.bot = bot
    self.chat_id = chat_id

  def _handle_message(self, topic, payload):
    message = payload.decode("utf-8")
    self.bot.send_message(self.chat_id, message)
