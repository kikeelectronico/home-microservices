FROM python:3.14.0rc1-slim-bullseye
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=80", "--workers=1"]