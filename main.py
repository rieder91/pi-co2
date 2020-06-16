import threading
import signal
import logging
from argparse import ArgumentParser
from blackboard import Blackboard
from gas import GasReader
from temp import TemperatureReader
from sound import SoundReader
from exporter import PrometheusExporter

threads = []
log_level = logging.INFO

# in some environments the sensor itself heats up skewing the temperature measurement. this variable allows you to
# counteract that. since the thermal output is constant a fixed offset is "good enough" for us (the sensor is not
# that accurate anyhow)
temp_offset = -1.5

# serial port for connection to the PT8005
sound_serial_port = "/dev/ttyUSB0"

parser = ArgumentParser()
parser.add_argument("-v", action="store_true")
options = parser.parse_args()
if options.v:
    log_level = logging.DEBUG

if __name__ == "__main__":
    log_format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=log_format, level=log_level, datefmt="%H:%M:%S")

    blackboard = Blackboard()

    gas = GasReader(blackboard)
    temperature = TemperatureReader(blackboard, temp_offset=temp_offset)
    sound = SoundReader(blackboard, serial_port=sound_serial_port)
    exporter = PrometheusExporter(blackboard)

    threads.append(threading.Thread(target=gas.measure, daemon=True))
    threads.append(threading.Thread(target=gas.set_baseline, daemon=True))
    threads.append(threading.Thread(target=gas.calibrate, daemon=True))
    threads.append(threading.Thread(target=temperature.measure, daemon=True))
    threads.append(threading.Thread(target=sound.measure, daemon=True))
    threads.append(threading.Thread(target=exporter.fill_gauges, daemon=True))

    exporter.start_prometheus_http_server()

    for thread in threads:
        thread.start()

    # noinspection PyUnusedLocal
    def bail_out(*args):
        logging.info("Received SIGTERM")
        gas.stop()
        temperature.stop()
        sound.stop()
        exporter.stop()
        logging.info("All threads stopped. Exiting")
        raise SystemExit(0)

    # noinspection PyTypeChecker
    signal.signal(signal.SIGTERM, bail_out)

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        bail_out()
