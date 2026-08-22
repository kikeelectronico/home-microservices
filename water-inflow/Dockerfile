FROM python:3.13.6-slim-bullseye
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "main.py"]
