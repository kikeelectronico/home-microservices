FROM python:3.13.6-slim-bullseye
COPY . /app
WORKDIR /app
RUN mkdir audio
RUN mkdir creds
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/creds/voice-alert.json"
RUN pip install -r requirements.txt
CMD python main.py