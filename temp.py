import board
import busio
import logging
import threading
from adafruit_htu21d import HTU21D


class TemperatureReader:
    def __init__(self, blackboard):
        self.stop_requested = False
        self.stop_event = threading.Event()

        self.blackboard = blackboard

        # initialize the sensor
        i2c = busio.I2C(board.SCL, board.SDA)
        self.htu21d = HTU21D(i2c)

    def stop(self):
        logging.info("TemperatureReader: Stop requested. Terminating threads")
        self.stop_requested = True
        self.stop_event.set()

    def measure(self, interval=10):
        logging.info("Starting temperature and humidity measurements at interval %s", interval)

        while not self.stop_requested:
            self.blackboard.set_temperature(self.htu21d.temperature)
            self.blackboard.set_humidity_in_percent(self.htu21d.relative_humidity)
            logging.debug("Temperature and relative humidity measured")
            self.stop_event.wait(interval)
