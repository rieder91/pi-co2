import time
import threading
import signal
import logging
from argparse import ArgumentParser
from blackboard import Blackboard
from gas import GasReader
from temp import TemperatureReader
from exporter import PrometheusExporter

threads = []
log_level = logging.INFO

parser = ArgumentParser()
parser.add_argument("-v", action="store_true")
options = parser.parse_args()
if options.v:
    log_level = logging.DEBUG

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=log_level, datefmt="%H:%M:%S")

    blackboard = Blackboard()

    gas = GasReader(blackboard)
    temperature = TemperatureReader(blackboard)
    exporter = PrometheusExporter(blackboard)

    threads.append(threading.Thread(target=gas.measure, daemon=True))
    threads.append(threading.Thread(target=gas.set_baseline, daemon=True))
    threads.append(threading.Thread(target=gas.calibrate, daemon=True))
    threads.append(threading.Thread(target=temperature.measure, daemon=True))
    threads.append(threading.Thread(target=exporter.fill_gauges, daemon=True))

    exporter.start_prometheus_http_server()

    for thread in threads:
        thread.start()
    
    def bail_out(*args):
        logging.info("Received SIGTERM")
        gas.stop()
        logging.info("All threads stopped. Exiting")
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, bail_out)

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        bail_out()

