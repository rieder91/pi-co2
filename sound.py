import logging
import re
import threading

import serial


class SoundReader:
    def __init__(self, blackboard, serial_port):
        self.stop_requested = False
        self.stop_event = threading.Event()

        self.blackboard = blackboard

        self.serial_port = serial_port

    def stop(self):
        logging.info("SoundReader: Stop requested. Terminating threads")
        self.stop_requested = True
        self.stop_event.set()

    def measure(self, interval=30):
        logging.info("Starting sound measurements at interval %s", interval)

        while not self.stop_requested:
            ser = serial.Serial(self.serial_port)
            ser.write(b'rec')
            ser.flush()
            value = 0
            count = 0
            for i in range(10):
                data = ser.read(64)
                match = re.search(b'\xA5\x0D', data)
                if match is not None:
                    offset = match.start()
                    if offset + 3 < len(data):
                        # first byte
                        v1 = data[offset + 2]
                        # second byte
                        v2 = data[offset + 3]
                        # convert two hex bytes two a decimal number
                        db_a = (int((v1 / 16)) * 10 + int((v1 % 16))) * 10
                        db_a += (int((v2 / 16)) * 10 + int((v2 % 16))) * 0.1
                        value += db_a
                        count += 1
                    else:
                        logging.warning("Sound level value index out-of-bounds")
            ser.write(b'rec')
            ser.flush()
            if value != 0 and count != 0:
                avg = value / count
                logging.debug("Sound level measured (%s)" % avg)
                self.blackboard.set_sound(avg)
            else:
                logging.warning("No sound measurement received")
            self.stop_event.wait(interval)
