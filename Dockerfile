FROM python:3.9.20-alpine3.19
USER pythonuser

# installation
COPY requirements.txt /app/requirements.txt
COPY main.py /app/main.py
RUN pip install -r requirements.txt

# environment variables
ENV PROMETHEUS_PORT=9099
ENV DEVICE_PATH="/dev/ttyUSB0"
ENV BAUD_RATE=9600
ENV TIMEOUT=1

# ports
EXPOSE 9099

# entrypoi
ENTRYPOINT ["python", "/app/main.py"]