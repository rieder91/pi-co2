import board
import busio
import logging
import threading
import os
import pickle
from adafruit_sgp30 import Adafruit_SGP30


class GasReader:

    def __init__(self, blackboard):
        self.__baseline_filename = "baseline.data"

        self.stop_requested = False
        self.stop_event = threading.Event()

        self.blackboard = blackboard

        # initialize the sensor
        i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        self.sgp30 = Adafruit_SGP30(i2c)
        self.sgp30.iaq_init()

        logging.debug("SPG30 serial #" + str([hex(i) for i in self.sgp30.serial]))

    def stop(self):
        logging.info("GasReader: Stop requested. Terminating threads")
        self.stop_requested = True
        self.stop_event.set()

    def measure(self, interval=10):
        logging.info("Starting gas measurements at interval %s", interval)

        while not self.stop_requested:
            self.blackboard.set_eco2(self.sgp30.eCO2)
            self.blackboard.set_tvoc(self.sgp30.TVOC)
            logging.debug("eCO2 and TVOC measured")
            self.stop_event.wait(interval)

    def set_baseline(self, interval=60*10):
        logging.info("Starting baseline management at interval %s", interval)

        e_co2_baseline, tvoc_baseline = None, None

        # read initial baseline from file
        if os.path.isfile(self.__baseline_filename):
            with open(self.__baseline_filename, "rb") as f:
                data = pickle.load(f)
                if "co2" in data:
                    e_co2_baseline = data.get("co2")
                if "tvoc" in data:
                    tvoc_baseline = data.get("tvoc")

        if e_co2_baseline is not None and tvoc_baseline is not None:
            logging.info("Read baseline from file")
        else:
            logging.info("No baseline found, using defaults")
            e_co2_baseline = 0x8c2e
            tvoc_baseline = 0x8d90

        logging.info("Setting baseline to eCO2=0x%x, TVOC=0x%x", e_co2_baseline, tvoc_baseline)
        self.sgp30.set_iaq_baseline(e_co2_baseline, tvoc_baseline)

        while not self.stop_requested:
            # write baseline to file
            with open(self.__baseline_filename, "wb") as f:
                co2, tvoc = self.sgp30.baseline_eCO2, self.sgp30.baseline_TVOC
                pickle.dump({"co2": co2, "tvoc": tvoc}, f)
                logging.debug("Saved baseline to file (0x%x, 0x%x)", co2, tvoc)
            self.stop_event.wait(interval)

    def calibrate(self, interval=60):
        logging.info("Starting gas sensor calibration at interval %s", interval)

        while not self.stop_requested:
            rh_mg = self.blackboard.get_humidity_in_mg()
            if rh_mg is None:
                logging.info("No humidity reading (yet), cannot calibrate gas sensor")
            else:
                # calibrate the gas sensor based on the humidity reading
                self.sgp30.set_iaq_humidity(rh_mg)
                logging.debug("Calibrated gas sensor based on humidity reading (%s)", rh_mg)
                
            self.stop_event.wait(interval)
