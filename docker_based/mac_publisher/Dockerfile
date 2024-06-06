FROM python:3.7-slim
WORKDIR /app
COPY mac_publisher/requirements.txt ./
RUN pip install -r requirements.txt
COPY src/ ./
CMD ["python","./mqtt_publish_mac.py"]