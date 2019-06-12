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

    def setECO2(self, value):
        self.__set__("eCO2", value)

    def getECO2(self):
        return self.storage.get("eCO2")

    def setTVOC(self, value):
        self.__set__("TVOC", value)

    def getTVOC(self):
        return self.storage.get("TVOC")

    def setHumidityInPercent(self, value):
        self.__set__("rhPercent", value)

    def getHumidityInMg(self):
        rhPercent = self.storage.get("rhPercent")
        temperature = self.storage.get("temperature")

        if rhPercent is not None and temperature is not None:
            # formula taken from https://carnotcycle.wordpress.com/2012/08/04/how-to-convert-relative-humidity-to-absolute-humidity/
            result = (6.112 * pow(math.e, (17.67 * temperature)/(temperature + 243.5)) * rhPercent * 2.1674) / (273.15 + temperature)
            return result
        else:
            logging.warn("Need both temperature and rhPercent to calculate humidity in mg/m3")
            return None

    def setTemperature(self, value):
        self.__set__("temperature", value)

    def getTemperature(self):
        return self.storage.get("temperature")

    def getHumidityInPercent(self):
        return self.storage.get("rhPercent")

    def dump(self):
        with self._lock:
            for key in self.storage:
                logging.info("%s = %s" % (key, self.storage.get(key)))
