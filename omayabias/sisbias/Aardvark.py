#!/usr/bin/python

from omayabias.logging import logger

from aardvark_py import *
from array import array

#from i2cdevices import *
#from array import array
#from xicor_functions import xicorpot

# VMIN = -9.87  # minimum output voltage from Xicor
# VMAX = 9.72   # maximum output voltage from Xicor
# VSENSE_GAIN = 200.0
# ISENSE_GAIN = 500.0
# Rs= 20.0
logger.name = __name__

def aardvark_error(mode):
    return aa_status_string(mode)

class Aardvark(object):
    """The usage class for the Aardvark I2C device"""
    def __init__(self, portnum, debug=True):
        """Find devices, open the portnum device
        and return"""
        self.debug = debug
        (num, ports) = aa_find_devices(16)
        if num > 0:
            self.port = ports[portnum]
            #unique_id = unique_ids[portnum]
            if (self.port & AA_PORT_NOT_FREE):
                self.port = self.port & ~AA_PORT_NOT_FREE
                logger.error("Port = %d, in-use not free" % self.port)
                if self.debug:
                    print "Port = %d, in-use not free" % self.port
                self.handle = -1
                return
            else:
                self.handle = aa_open(self.port)
                if self.handle > 0:
                    if self.debug:
                        print "Port = %d, available, handle = %d" % (self.port, self.handle)
                    logger.info("Port = %d, available, handle = %d" % (self.port, self.handle))
                    self.configure(AA_CONFIG_SPI_I2C)
                    self.target_power(AA_TARGET_POWER_BOTH)
                    self.i2c_pullup(AA_I2C_PULLUP_NONE)
                    self.i2c_bitrate(400)
                else:
                    if self.debug:
                        print "%s" % aardvark_error(self.handle)
                    logger.error("%s" % aardvark_error(self.handle))
            return
        else:
            if self.debug:
                print "No Aardvark devices found. %s" % aardvark_error(num)
            logger.error("No Aardvark devices found. %s" % aardvark_error(num))
            self.handle = -1
            return

    def configure(self, mode):
        if self.debug:
            logger.debug("Configuring I2C device %s" % self.handle)
        self.config = aa_configure(self.handle, mode)
        return self.config

    def target_power(self, power_mask):
        if self.debug:
            logger.debug("Setting Target Power on device %s" % self.handle)
        self.pin_status = aa_target_power(self.handle, power_mask)
        return self.pin_status

    def i2c_pullup(self, pullup_mask):
        if self.debug:
            logger.debug("Setting I2C pullup to NONE on %s" % self.handle)
        self.bus_status = aa_i2c_pullup(self.handle, pullup_mask)
        return self.bus_status

    def i2c_bitrate(self, bitrate):
        if self.debug:
            logger.debug("Set I2C bitrate on %s to %s" % (self.handle, bitrate))
        self.bitrate = aa_i2c_bitrate(self.handle, bitrate)
        return self.bitrate

    def close(self):
        if self.debug:
            logger.debug("Closing %s" % self.handle)
        return aa_close(self.handle)

    def reopen(self):
        if self.debug:
            logger.debug("Closing and re-opening Aardvard device %s" % self.handle)
        rtn = aa_close(self.handle)
        self.handle = aa_open(self.port)

    def check_write_count(self, count, num_written, msg=' '):
        if (count < 0):
            if self.debug:
                print "%s error: %s" % (msg, aa_status_string(count))
            logger.error("%s error: %s" % (msg, aa_status_string(count)))
            return -1
        elif (count == 0):
            if self.debug:
                print "%s error: no bytes written" % msg
                print "  are you sure you have the right slave address?"
            logger.error("%s error: no bytes written" % msg)
            logger.error("  are you sure you have the right slave address?")
            return -1
        elif (count != num_written):
            if self.debug:
                print "%s error: only a partial number of bytes written" % msg
                print "  (%d) instead of full (%d)" % (count, num_written)
            logger.error("%s error: only a partial number of bytes written" % msg)
            logger.error("  (%d) instead of full (%d)" % (count, num_written))
            return -1
        else:
            return 0

    def check_read_count(self, count, num_toberead, msg=' '):
        if (count < 0):
            if self.debug:
                print "%s error: %s" % (msg, aa_status_string(count))
            logger.error("%s error: %s" % (msg, aa_status_string(count)))
            return -1
        elif (count == 0):
            if self.debug:
                print "%s error: no bytes read" % msg
                print "  are you sure you have the right slave address?"
            logger.error("%s error: no bytes read" % msg)
            logger.error("  are you sure you have the right slave address?")
            return -1
        elif (count != num_toberead):
            if self.debug:
                print "%s error: read a partial number of bytes" % msg
                print "  (%d) instead of full (%d)" % (count, num_toberead)
            logger.error("%s error: read a partial number of bytes" % msg)
            logger.error("  (%d) instead of full (%d)" % (count, num_toberead))
            return -1
        else:
            return 0

    def i2c_write(self, address, data, flags=AA_I2C_NO_FLAGS):
        data_out = array('B', data)
        count = aa_i2c_write(self.handle, address, flags, data_out)
        ret = self.check_write_count(count, len(data_out))
        if ret == -1:
            raise
        #if self.debug:
        #    logger.debug("Wrote %d bytes: %s" % (len(data_out), data))

    def i2c_read(self, address, read_count, flags=AA_I2C_NO_FLAGS):
        (count, data_in) = aa_i2c_read(self.handle, address, flags,
                                       read_count)
        ret = self.check_read_count(count, read_count)
        if ret == -1:
            raise
        #if self.debug:
        #    logger.debug("Read %d bytes %s" % (len(data_in), data_in))
        return data_in
    
    # def SetMode_PCA(self, mode):
    #     """Sets CV or CR mode on the Philips PCA device"""
    #     dout = [0x03,0x00] #sets the configuration register as all outputs
    #     data_out = array('B', dout)
    #     count = aa_i2c_write(self.handle, PCA_ADDRESS, AA_I2C_NO_FLAGS,
    #                          data_out)
    #     self.check_write_count(count, len(data_out))
    #     if mode == CVMODE:
    #         data_out = array('B', [0x01, 0x00])
    #     elif mode == CRMODE:
    #         data_out = array('B', [0x01, 0xFF])
    #     count = aa_i2c_write(self.handle, PCA_ADDRESS, AA_I2C_NO_FLAGS,
    #                          data_out)
    #     self.check_write_count(count, len(data_out))        

    # def set_voltage(self, channel, voltage):
    #     """Sets mixer voltage for given channel"""
    #     self.xicor.insert(channel,xicorpot(channel, voltage))
    #     for i in range(4):
    #         if self.xicor[channel].pot[i] != self.xicor_prev_pot[channel][i]:
    #             data_out = array('B', [X9241A_POT_ADDRESS[i],self.xicor[channel].pot[i]])
    #             count = aa_i2c_write(self.handle, X9241A_MIXER_ADDRESS[channel],
    #                                  AA_I2C_NO_FLAGS, data_out)
    #             self.check_write_count(count, len(data_out), 'pot%1d' % i)
    #     self.xicor_prev_pot[channel] = self.xicor[channel].pot

    # def Initialize_ADC(self, chipnumber, channel):
    #     """There are 2 chips in each ADC and 4 channels.
    #     This function initializes it.
    #     channel should start at 0"""
    #     data_out = array('B', [ADC_MODE2_CH[channel]])
    #     count = aa_i2c_write(self.handle, ADC_ADDRESS[chipnumber],
    #                          AA_I2C_NO_FLAGS, data_out)
    #     self.check_write_count(count, len(data_out),
    #                            'ADC init chip %d, channel %d' % (chipnumber,channel))

    # def Read_ADC(self, chipnumber, channel):
    #     self.Initialize_ADC(chipnumber, channel)
    #     (count, data_in) = aa_i2c_read(self.handle, ADC_ADDRESS[chipnumber],
    #                                    AA_I2C_NO_FLAGS, 2)
    #     self.check_read_count(count, 2,
    #                           'Read_ADC chip %d, channel %d' % (chipnumber, channel))
    #     if count == 2:
    #         msb = (data_in[0]&0x000f)<<8
    #         lsb = (data_in[1]&0x00ff)
    #         adc_value = msb+lsb
    #         return adc_value

    # def read_Vsense(self, chipnumber):
    #     adc_value = self.Read_ADC(chipnumber, 0)
    #     print adc_value
    #     adc_step = (VMAX - VMIN)/4096.
    #     return ((adc_value * adc_step) + VMIN)/VSENSE_GAIN

    # def read_Isense(self, chipnumber):
    #     adc_value = self.Read_ADC(chipnumber, 0)
    #     print adc_value
    #     adc_step = (VMAX - VMIN)/4096.
    #     return ((adc_value * adc_step) + VMIN)/(ISENSE_GAIN * Rs)
