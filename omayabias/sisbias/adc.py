from omayabias.logging import logger

logger.name = __name__

# ADC
ADC_ADDRESS = [0x21, 0x22]
#ADC2_ADDRESS = 0x22
ADC1_CONFIG_REG_ADDRESS = 0x82
ADC1_CONVERSION_REG_ADDRESS = 0x80
ADC_MODE2_CH = [0x80, 0x90, 0xa0, 0xb0]

VMIN = -9.87  # minimum output voltage from Xicor
VMAX = 9.72   # maximum output voltage from Xicor
VSENSE_GAIN = 200.0
ISENSE_GAIN = 500.0
Rs= 20.0

class ADC(object):
    def __init__(self, aardvark, debug=False):
        self.ad = aardvark # The Aardvark device instance
        self.debug = debug

    def initialize_ADC(self, chipnumber, channel):
        """There are 2 chips in each ADC and 4 channels.
        This function initializes it.
        channel should start at 0"""
        dout = [ADC_MODE2_CH[channel]]
        self.ad.i2c_write(ADC_ADDRESS[chipnumber], dout)
        if self.debug:
            print "Initialized ADC Chipnumber %d in channel %d" % (chipnumber, channel)
        logger.debug("Initialized ADC Chipnumber %d in channel %d" % (chipnumber, channel))

    def read_ADC(self, chipnumber, channel):
        self.initialize_ADC(chipnumber, channel)
        data_in = self.ad.i2c_read(ADC_ADDRESS[chipnumber], 2)
        if len(data_in) == 2:
            msb = (data_in[0] & 0x000f) << 8
            lsb = (data_in[1] & 0x00ff)
            adc_value = msb + lsb
            return adc_value

    def read_Vsense(self, channel):
        adc_value = self.read_ADC(0, channel)
        if self.debug:
            logger.debug("VSense ADC counts: %d" % adc_value)
        adc_step = (VMAX - VMIN)/4096.
        return ((adc_value * adc_step) + VMIN)/VSENSE_GAIN

    def read_Isense(self, channel, Rs=20):
        adc_value = self.read_ADC(1, channel)
        if self.debug:
            logger.debug("ISense ADC counts: %d" % adc_value)
        adc_step = (VMAX - VMIN)/4096.
        return ((adc_value * adc_step) + VMIN)/(ISENSE_GAIN * Rs)

            


