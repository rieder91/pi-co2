import time
import board
import busio
import logging
import threading
from adafruit_sgp30 import Adafruit_SGP30

class GasReader:
    def __init__(self, blackboard):
        self.stop_requested = False
        self.stop_event = threading.Event()

        self.blackboard = blackboard

        # initialize the sensor
        i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        self.sgp30 = Adafruit_SGP30(i2c)
        self.sgp30.iaq_init()

        logging.debug("SPG30 serial #" + str([hex(i) for i in self.sgp30.serial]))

    def stop(self):
        logging.info("GasReader: Stop requested. Terminitating threads")
        self.stop_requested = True
        self.stop_event.set()

    def measure(self, interval=10):
        logging.info("Starting gas measurements at interval %s", interval)

        while not self.stop_requested:
            self.blackboard.setECO2(self.sgp30.eCO2)
            self.blackboard.setTVOC(self.sgp30.TVOC)
            logging.debug("eCO2 and TVOC measured")
            self.stop_event.wait(interval)

    def set_baseline(self, interval=60*60):
        logging.info("Starting baseline management at interval %s", interval)

        # TODO read initial baseline from file
        eCO2_baseline, tvoc_baseline = None, None
        if eCO2_baseline is not None and tvoc_baseline is not None:
            logging.debug("Read baseline from file")
        else:
            logging.debug("No baseline found, using defaults")
            eCO2_baseline = 0x8c2e
            tvoc_baseline = 0x8d90

        logging.info("Setting baseline to eCO2=0x%x, TVOC=0x%x", eCO2_baseline, tvoc_baseline)
        self.sgp30.set_iaq_baseline(eCO2_baseline, tvoc_baseline)

        while not self.stop_requested:
            new_eCO2_baseline, new_tvoc_baseline = self.sgp30.baseline_eCO2, self.sgp30.baseline_TVOC
            if eCO2_baseline != new_eCO2_baseline or tvoc_baseline != new_tvoc_baseline:
                # TODO write baseline to file
                logging.debug("Saved baseline to file")
            self.stop_event.wait(interval)

    def calibrate(self, interval=60):
        logging.info("Starting gas sensor calibration at interval %s", interval)

        while not self.stop_requested:
            rhMg = self.blackboard.getHumidityInMg()
            if rhMg is None:
                logging.info("No humidity reading, cannot calibrate gas sensor")
            else:
                # TODO calibrate the gas sensor based on the humidity reading (need to convert RH% to mg/m3)
                logging.debug("Calibrated gas sensor based on humidity reading")
                
            self.stop_event.wait(interval)
        
