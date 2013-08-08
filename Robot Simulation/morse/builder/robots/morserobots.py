import logging; logger = logging.getLogger("morserobots." + __name__)

from morse.builder import Robot

class ATRV(Robot):
    def __init__(self, name=None):
        Robot.__init__(self, "atrv")
        self.name = name
        self.properties(classpath = "morse.robots.atrv.ATRVClass")

