#!/usr/bin/python

from omayabias.logging import logger
logger.name = __name__

# Xicor 
X9241A_POT_ADDRESS = [0xa0, 0xa4, 0xa8, 0xac]
X9241A_MIXER_ADDRESS = [0x28, 0x29]

VMIN = -9.87  # minimum output voltage from Xicor
VMAX = 9.72   # maximum output voltage from Xicor

def dut_voltage(bias_voltage, Rp=100., Rs=20., Rd=50.,
                Rb=10e3):
    """
    Given a bias voltage, determines the voltage drop 
    across the Device Under Test (DUT)
    """
    Req = (Rp * (Rs + Rd))/(Rp + Rs + Rd)
    Veq = (Req/(Req+Rb)) * bias_voltage
    Vdut = (Rd/(Rd+Rs)) * Veq
    return Vdut

class XicorPot(object):
    """The usage class for the Xicor X9241A quad digital potentiometer"""
    def __init__(self, aardvark, channel, position=None,
                 debug=False):
        # device handle
        self.ad = aardvark
        self.channel = channel
        self.debug = debug
        self.pot = [1,1,1,1] #just initialize
        self.current_position = None
        if position is not None:
            self.set_position(position)
        else:
            self.set_position(1)
            
    def set_position(self, position):
        if position < 1:
            position = 1
        if position > 8001:
            position = 8001
        if self.current_position is None:
            # no current position known
            self.set_quadpots(position)
        elif position != self.current_position:
            self.set_quadpots(position)

            
    def set_mixer_voltage(self, mixer_voltage):
        self.mixer_voltage = mixer_voltage
        #VS_ADC_count = (mixer_voltage + 50.566)/0.0248
        #self.xicor_count = int((VS_ADC_count-124.79)/0.475)
        Vdmin, Vdmax = dut_voltage(VMIN), dut_voltage(VMAX)
        xicor_step = (Vdmax - Vdmin)/8001.
        self.xicor_count = int((mixer_voltage - Vdmin)/xicor_step)
        #check to see that position is less than 8064
        self.xicor_count = self.xicor_count<8001 and self.xicor_count or 8000
        #check to see that position is greater than or equal 0
        self.xicor_count = self.xicor_count>=0 and self.xicor_count or 0
        self.wcr_range_cascade_setting(self.xicor_count)
        self.wcr_setting_from_range_cascade()
        if self.debug:
            print self.xicor_count, self.wiper_range, self.wiper_cascade
        self.set_position(self.xicor_count)
        #self.v_channel=((self.xicor_count*5.0/8064.0)-OFFSET)*AMPLIFIER_GAIN
        
    def wcr_range_cascade_setting(self, position):
        """gets WCR (wiper control register) range
        and cascade setting from the integer value of position"""
        self.wiper_range = position/128
        self.wiper_cascade = position % 128
    
    def wcr_setting_from_range_cascade(self):
        """gets values of 4 pots from range and cascade"""
        self.pot[0] = self.wiper_range
        self.pot[3] = self.wiper_range+1
        if self.wiper_cascade > 63:
            self.pot[2] = self.wiper_cascade-64
            self.pot[1] = 64
        else:
            self.pot[2] = 0
            self.pot[1] = self.wiper_cascade
            
    def set_quadpots(self, position):
        if self.debug:
            print "Setting quadpot position %d" % position
        logger.debug("Setting quadpot position %d" % position)
        self.wcr_range_cascade_setting(position)
        self.wcr_setting_from_range_cascade()
        for i in range(4):
            self.ad.i2c_write(X9241A_MIXER_ADDRESS[self.channel],
                              [X9241A_POT_ADDRESS[i], self.pot[i]])
        self.current_position = position
