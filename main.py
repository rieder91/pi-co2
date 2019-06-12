import time
import threading
import signal
import logging
from blackboard import Blackboard
from gas import GasReader

threads = []
if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.DEBUG, datefmt="%H:%M:%S")

    blackboard = Blackboard()

    gas = GasReader(blackboard)
    # TODO temperature = TemperatureReader(blackboard)

    threads.append(threading.Thread(target=gas.measure, daemon=True))
    threads.append(threading.Thread(target=gas.set_baseline, daemon=True))
    threads.append(threading.Thread(target=gas.calibrate, daemon=True))

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

