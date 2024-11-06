from smllib import SmlStreamReader
import serial
import os
from prometheus_client import start_http_server, Summary, Gauge, Info, Counter

port = int(os.environ.get('PROMETHEUS_PORT', 9099))
device_path = os.environ.get('DEVICE_PATH', '/dev/ttyUSB0')
baudrate = os.environ.get('BAUD_RATE', 9600)
device = os.environ.get('DEVICE', "smartmeter")
obis_values = os.environ.get('OBIS_VALUES', "0100020800ff,0100100700ff,0100010800ff")

obis_values = obis_values.split(",")

stream = SmlStreamReader()
ser = serial.Serial(device_path, baudrate=baudrate)
INFO = Info('Smartmeter_Prometheus_Adapter', 'This adapter gives energy metrics about the heat pump')
CURRENT_ENERGY = Gauge('current_energy_watts', 'This is the current energy drawn from the grid', ["name", "metric", "unit"])
TOTAL_ENERGY = Gauge("total_energy_watthours", "This is the total energy received from the grid", ["name", "metric", "unit"])
TOTAL_ENERGY_FEED = Gauge("total_energy_feed_watthours", "This is the total energy fed to the grid", ["name", "metric", "unit"])

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(port)
    print("Server started...")
    print(f"Name of the monitored device:\t{device}")
    print(f"listening on port:\t{port}")
    print(f"reading from: \t{device_path}")
    print(f"with baudrate of: \t{baudrate}")
    # Generate some requests.
    try:
        while True:
            # Read bytes from the serial port
            data = ser.read(32)  # Read up to 32 bytes at a time
            stream.add(data)
            sml_frame = stream.get_frame()
            if sml_frame is not None:
                obis_values = sml_frame.get_obis()
                TOTAL_ENERGY.labels(name=device, metric="total_energy", unit="Wh").set(obis_values[2].value)
                TOTAL_ENERGY_FEED.labels(name=device, metric="total_energy", unit="Wh").set(obis_values[3].value)
                CURRENT_ENERGY.labels(name=device, metric="current_energy", unit="W").set(obis_values[4].value)

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        # Close the serial port
        ser.close()
        print("Serial port closed.")