"""
Master wrapper for all I2C devices in 
OMAyA Bias System
"""

from omayabias.logging import logger
from omayabias.utils import OMAYAGeneralError
from .Aardvark import Aardvark
from .pca import PCA
from .adc import ADC
from .xicor_potentiometer import XicorPot

logger.name = __name__

class SISBias(object):
    def __init__(self, portnum=0, debug=False):
        self.debug = debug
        self.portnum = portnum
        self.ad = Aardvark(self.portnum)
        if self.ad.handle == -1:
            raise OMAYAGeneralError("Aardvark Device in Use")
        self.pca = PCA(self.ad, debug=self.debug)
        self.adc = ADC(self.ad, debug=self.debug)
        self.xicor = {}
        for channel in range(2):
            self.xicor[channel] = XicorPot(self.ad, channel)
        
