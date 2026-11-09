import functions


class TelegramBotService:

  def __init__(self):
    self.settings = None
    self.bot = None
    self.storage_client = None

  def initialize(self, settings, bot, storage_client):
    self.settings = settings
    self.bot = bot
    self.storage_client = storage_client

  # Commands handler
  def _send_welcome(self, message):
    command = message.text.split()[0]

    if command == '/start':
      self.bot.reply_to(message, "Hi, I am Maguna")
    elif command == '/help':
      self.bot.reply_to(message, "I am sorry but I don't know you.")
    else:
      if str(message.from_user.id) == self.settings.enrique_chat_id:
        if command == '/test':
          # Test an authenticated command
          response = functions.test()
          self.bot.send_message(self.settings.enrique_chat_id, response, parse_mode='Markdown')
        elif command == '/home':
          # Test Homeware API and db
          response = functions.getHomewareTest(self.settings.homeware_api_url, self.settings.homeware_api_key)
          self.bot.send_message(self.settings.enrique_chat_id, "Corriendo" if response else "Caido", parse_mode='Markdown')
        elif command == '/directions':
          # Get the public IP
          response = functions.getPublicIP(self.settings.get_ip_endpoint)
          self.bot.send_message(self.settings.enrique_chat_id, response, parse_mode='Markdown')
      else:
        self.bot.reply_to(message, "I am sorry but I don't know you.")

  # Global handler
  def _echo_message(self, message):
    if str(message.from_user.id) == self.settings.enrique_chat_id:
      # Download the YouTube video once the URL is given
      if "youtube.com" in message.text or "youtu.be" in message.text:
        self.bot.send_message(self.settings.enrique_chat_id, "Descargando...", parse_mode='Markdown')
        url = message.text
        urls = functions.downloadYouTubeVideo(url, self.storage_client, self.settings.bucket_name)
        self.bot.send_message(self.settings.enrique_chat_id, "Lo tenemos", parse_mode='Markdown')
        for url in urls:
          self.bot.send_message(self.settings.enrique_chat_id, url, parse_mode='Markdown')

  def register_handlers(self):
    self.bot.message_handler(commands=['start', 'help','test','home','directions'])(self._send_welcome)
    self.bot.message_handler(func=lambda message: True)(self._echo_message)
