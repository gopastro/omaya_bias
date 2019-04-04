from omayabias.logging import logger

logger.name = __name__

PCA_ADDRESS = 0x20
CVMODE = 0
CRMODE = 1

class PCA(object):
    def __init__(self, aardvark, debug=True):
        self.ad = aardvark # The Aardvark device instance
        self.debug = debug
        
    def SetMode(self, mode):
        """Sets CV or CR mode on the Philips PCA device"""
        dout = [0x03,0x00] #sets the configuration register as all outputs
        self.ad.i2c_write(PCA_ADDRESS, dout)
        if mode == CVMODE:
            dout = [0x01, 0x00]
            mode_text = 'CVMODE'
        elif mode == CRMODE:
            dout = [0x01, 0xFF]
            mode_text = 'CRMODE'
        if self.debug:
            print "Setting PCA to %s" % mode_text
        logger.debug("Setting PCA to %s" % mode_text)
        self.ad.i2c_write(PCA_ADDRESS, dout)

        
