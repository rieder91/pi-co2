from threading import Lock
import logging

class Blackboard:
    def __init__(self):
        self.storage = {}
        self._lock = Lock()
    
    def set(self, key, value):
        with self._lock:
            self.storage[key] = value
        logging.debug("Set key '%s' to value '%s'" % (key, value))

    def get(self, key):
        return self.storage.get(key)

    def setECO2(self, value):
        with self._lock:
            self.storage["eCO2"] = value

    def getECO2(self):
        return self.storage.get("eCO2")

    def setTVOC(self, value):
        with self._lock:
            self.storage["TVOC"] = value

    def getTVOC(self):
        return self.storage["TVOC"]

    def setHumidityInPercent(self, value):
        with self._lock:
            self.storage["rhPercent"] = value

    def getHumidityInMg(self):
        rhPercent = self.storage.get("rhPercent")
        if rhPercent is not None:
            # TODO convert humidity from percent to mg/m3
            return None
        else:
            return None

    def dump(self):
        with self._lock:
            for key in self.storage:
                logging.info("%s = %s" % (key, self.storage.get(key)))
