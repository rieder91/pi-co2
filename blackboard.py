from threading import Lock
import logging
import math


class Blackboard:
    def __init__(self):
        self.storage = {}
        self._lock = Lock()
    
    def __set__(self, key, value):
        with self._lock:
            self.storage[key] = value
        logging.debug("Set key '%s' to value '%s'" % (key, value))

    def get(self, key):
        return self.storage.get(key)

    def set_eco2(self, value):
        self.__set__("eCO2", value)

    def get_eco2(self):
        return self.storage.get("eCO2")

    def set_tvoc(self, value):
        self.__set__("TVOC", value)

    def get_tvoc(self):
        return self.storage.get("TVOC")

    def set_humidity_in_percent(self, value):
        self.__set__("rhPercent", value)

    def get_humidity_in_mg(self):
        rh_percent = self.storage.get("rhPercent")
        temperature = self.storage.get("temperature")

        if rh_percent is not None and temperature is not None:
            # formula based on:
            # https://carnotcycle.wordpress.com/2012/08/04/how-to-convert-relative-humidity-to-absolute-humidity/
            result = (6.112 * pow(math.e, (17.67 * temperature)/(temperature + 243.5)) * rh_percent * 2.1674) / (273.15 + temperature)
            return result
        else:
            logging.debug("Need both temperature and rhPercent to calculate humidity in mg/m3")
            return None

    def set_temperature(self, value):
        self.__set__("temperature", value)

    def get_temperature(self):
        return self.storage.get("temperature")

    def get_humidity_in_percent(self):
        return self.storage.get("rhPercent")

    def dump(self):
        with self._lock:
            for key in self.storage:
                logging.info("%s = %s" % (key, self.storage.get(key)))
