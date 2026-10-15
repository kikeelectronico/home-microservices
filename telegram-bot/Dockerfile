FROM python:3.14.0rc1-slim-bullseye
COPY . /app
WORKDIR /app
RUN mkdir creds
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/creds/telegram-bot.json"
RUN pip install -r requirements.txt
CMD ["python", "main.py"]