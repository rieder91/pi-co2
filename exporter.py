import threading
import logging
from prometheus_client import Gauge, start_http_server


class PrometheusExporter:
    def __init__(self, blackboard):
        self.stop_requested = False
        self.stop_event = threading.Event()

        self.blackboard = blackboard

        self.temperature_gauge = Gauge("temperature_celsius", "Room temperature in degrees celsius")
        self.humidity_percent_gauge = Gauge("humidity_percent", "Relative Humidity in percent")
        self.humidity_mg_gauge = Gauge("humidity_mg", "Humidity in mg/m^3")

        self.co2_gauge = Gauge("co2", "CO2 in in ppm")
        self.tvoc_gauge = Gauge("tvoc", "Total volatile organic compound in ppm")

    def stop(self):
        logging.info("PrometheusExporter: Stop requested. Terminating threads")
        self.stop_requested = True
        self.stop_event.set()

    def fill_gauges(self, interval=10):
        logging.info("Updating prometheus gauges at interval %s", interval)

        while not self.stop_requested:
            t = self.blackboard.get_temperature()
            if t:
                self.temperature_gauge.set(t)

            rh_p = self.blackboard.get_humidity_in_percent()
            if rh_p:
                self.humidity_percent_gauge.set(rh_p)

            rh_mg = self.blackboard.get_humidity_in_mg()
            if rh_mg:
                self.humidity_mg_gauge.set(rh_mg)

            co2 = self.blackboard.get_eco2()
            if co2:
                self.co2_gauge.set(co2)

            tvoc = self.blackboard.get_tvoc()
            if tvoc:
                self.tvoc_gauge.set(tvoc)

            logging.debug("Set prometheus gauges to current values")

            self.stop_event.wait(interval)

    def start_prometheus_http_server(self, port=8000):
        logging.info("Starting prometheus http server on port %s", port)
        start_http_server(port)
