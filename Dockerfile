FROM python:3.9.20-alpine3.19

RUN adduser -D -h /home/pythonuser -s /bin/bash pythonuser
RUN addgroup pythonuser dialout

# installation
COPY requirements.txt /app/requirements.txt
COPY main.py /app/main.py
WORKDIR /app
RUN pip install -r requirements.txt

RUN chown -R pythonuser:pythonuser /app

USER pythonuser

# environment variables
ENV PROMETHEUS_PORT=9099
ENV DEVICE_PATH="/dev/ttyUSB0"
ENV BAUD_RATE=9600
ENV TIMEOUT=1
ENV DEVICE="smartmeter"
ENV OBIS_VALUES="0100020800ff,0100100700ff,0100010800ff"

# 0100020800ff total feed to grid
# 0100100700ff current energy
# 0100010800ff total energy from grid

# ports
EXPOSE 9099

# entrypoi
ENTRYPOINT ["python", "/app/main.py"]