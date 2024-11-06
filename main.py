from smllib import SmlStreamReader
import serial
import os
from prometheus_client import start_http_server, Summary, Gauge, Info, Counter

port = int(os.environ.get('PROMETHEUS_PORT', 9099))
device_path = os.environ.get('DEVICE_PATH', '/dev/ttyUSB0')
baudrate = os.environ.get('BAUD_RATE', 9600)
timeout = os.environ.get('TIMEOUT', 1)

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')


stream = SmlStreamReader()
ser = serial.Serial(device_path, baudrate=baudrate, timeout=timeout)
INFO = Info('Smartmeter_Prometheus_Adapter', 'This adapter gives energy metrics about the heat pump')
CURRENT_ENERGY = Gauge('heat_pump_current_energy_watts', 'This is the current energy drawn from the grid', ["name", "metric", "unit"])
TOTAL_ENERGY = Gauge("heat_pump_total_energy_watthours", "This is the total energy received from the grid", ["name", "metric", "unit"])

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(port)
    # Generate some requests.
    try:
        while True:
            # Read bytes from the serial port
            data = ser.read(32)  # Read up to 32 bytes at a time
            stream.add(data)
            sml_frame = stream.get_frame()
            if sml_frame is None:
                print('Bytes missing')
            else:
                obis_values = sml_frame.get_obis()
                TOTAL_ENERGY.labels(name="heat_pump", metric="total_energy", unit="Wh").set(obis_values[2].value)
                CURRENT_ENERGY.labels(name="heat_pump", metric="current_energy", unit="W").set(obis_values[4].value)
                print(obis_values[2].value) # total energy from grid (Wh)
                print(obis_values[4].value) # current energy from grid (W)
                #parsed_msgs = sml_frame.parse_frame()
                #for msg in parsed_msgs:
                    #print(msg.format_msg())

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        # Close the serial port
        ser.close()
        print("Serial port closed.")