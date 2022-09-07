#!/usr/bin/python

#*****************************************************************************
# UpbeatLabs_MCP39F521.py
#
# This is a library for the Upbeat Labs Dr. Wattson Energy Monitoring Board
# --> https://www.protostax.com/products/dr-wattson-energy-monitoring-board-v2/
#
# Written by Sridhar Rajagopal for Upbeat Labs LLC.
#
# BSD 3-Clause License

# Copyright (c) 2018, Upbeat Labs
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#*****************************************************************************

from smbus2 import SMBus, i2c_msg
import time
import logging
from enum import Enum
import struct


# MCP39F521 default address.
MCP39F521_I2CADDR           = 0x74
DEFAULT_BUSNUM              = 1 


# These can be implemented as namedtuples, or as of python 3.7, dataclasses
# There are some known performance issues with regards to continually creating
# namedtuples (as would be the case for polling energy data)
# so leaving these as classes for now
# XXX : TODO Revisit

class UpbeatLabs_MCP39F521_Data(object):
    def __init__(self, systemStatus = None, systemVersion = None, voltageRMS = None,
                lineFrequency = None, analogInputVoltage = None,
                powerFactor = None, currentRMS = None,
                activePower = None, reactivePower = None, apparentPower = None):
        self.systemStatus = systemStatus
        self.systemVersion = systemVersion
        self.voltageRMS = voltageRMS
        self.lineFrequency = lineFrequency
        self.analogInputVoltage = analogInputVoltage
        self.powerFactor = powerFactor
        self.currentRMS = currentRMS
        self.activePower =  activePower
        self.reactivePower = reactivePower
        self.apparentPower = apparentPower
    
class UpbeatLabs_MCP39F521_AccumData(object):
    def __init__(self, activeEnergyImport = None, activeEnergyExport = None,
                reactiveEnergyImport = None, reactiveEnergyExport = None):
        self.activeEnergyImport = activeEnergyImport
        self.activeEnergyExport = activeEnergyExport
        self.reactiveEnergyImport = reactiveEnergyImport
        self.reactiveEnergyExport = reactiveEnergyExport       

        
class UpbeatLabs_MCP39F521_CalibrationData(object):
    def __init__(self, calibrationRegisterDelimiter = None, gainCurrentRMS = None,
                gainVoltageRMS = None, gainActivePower = None,
                gainReactivePower = None, offsetCurrentRMS = None,
                offsetActivePower = None, offsetReactivePower = None,
                dcOffsetCurrent = None, phaseCompensation = None,
                apparentPowerDivisor = None):
        self.calibrationRegisterDelimiter = calibrationRegisterDelimiter
        self.gainCurrentRMS = gainCurrentRMS
        self.gainVoltageRMS = gainVoltageRMS
        self.gainActivePower = gainActivePower 
        self.gainReactivePower = gainReactivePower
        self.offsetCurrentRMS = offsetCurrentRMS
        self.offsetActivePower = offsetActivePower
        self.offsetReactivePower = offsetReactivePower
        self.dcOffsetCurrent = dcOffsetCurrent
        self.phaseCompensation = phaseCompensation
        self.apparentPowerDivisor = apparentPowerDivisor    

    
class UpbeatLabs_MCP39F521_DesignConfigData(object):
    def __init__(self, rangeVoltage = None, rangeCurrent = None,
                rangePower = None, rangeUnimplemented = None,
                calibrationCurrent = None, calibrationVoltage = None,
                calibrationPowerActive = None, calibrationPowerReactive = None,
                lineFrequencyRef = None):
        self.rangeVoltage = rangeVoltage
        self.rangeCurrent = rangeCurrent
        self.rangePower = rangePower
        self.rangeUnimplemented = rangeUnimplemented 
        self.calibrationCurrent = calibrationCurrent
        self.calibrationVoltage = calibrationVoltage
        self.calibrationPowerActive = calibrationPowerActive
        self.calibrationPowerReactive = calibrationPowerReactive
        self.lineFrequencyRef = lineFrequencyRef        


class UpbeatLabs_MCP39F521_EventFlagLimits(object):
    def __init__(self, voltageSagLimit = None, voltageSurgeLimit = None,
                overCurrentLimit = None, overPowerLimit = None):
        self.voltageSagLimit = voltageSagLimit
        self.voltageSurgeLimit = voltageSurgeLimit
        self.overCurrentLimit = overCurrentLimit
        self.overPowerLimit = overPowerLimit
        

class UpbeatLabs_MCP39F521_CalibrationConfig(object):
    def __init__(self, systemConfig = None, accumInt = None, designConfigData = None,
                     gainCurrentRMS = None, gainVoltageRMS = None, gainActivePower = None,
                     gainReactivePower = None, phaseCompensation = None):
        self.systemConfig = systemConfig
        self.accumInt = accumInt
        self.designConfigData = designConfigData
        self.gainCurrentRMS = gainCurrentRMS
        self.gainVoltageRMS = gainVoltageRMS
        self.gainActivePower = gainActivePower
        self.gainReactivePower = gainReactivePower
        self.phaseCompensation = phaseCompensation


calibConfig = [
    UpbeatLabs_MCP39F521_CalibrationConfig(268435456, 5, UpbeatLabs_MCP39F521_DesignConfigData(18, 15, 22, 0, 8456, 1203, 9920, 1101, 60000), 40386, 57724, 50987, 45458, 208),
    UpbeatLabs_MCP39F521_CalibrationConfig(268435456, 5, UpbeatLabs_MCP39F521_DesignConfigData(18, 13, 20, 27, 20000, 1200, 24000, 20785, 60000), 33247, 57917, 42529, 38181, 0),
    UpbeatLabs_MCP39F521_CalibrationConfig(268435456, 5, UpbeatLabs_MCP39F521_DesignConfigData(18, 13, 20, 27, 17100, 1218, 20800, 5470, 60000), 50090, 57394, 63413, 57227, 58),
    UpbeatLabs_MCP39F521_CalibrationConfig(268435456, 5, UpbeatLabs_MCP39F521_DesignConfigData(18, 13, 20, 27, 17031, 1207, 20611, 8327, 59488), 49919, 58063, 64169, 57325, 6)
    ]
    
        
class UpbeatLabs_MCP39F521(object):
    """Class for communicating with an MCP39F521 device like Dr. Wattson using the 
    python smbus library."""
    class Error_code(Enum):
        SUCCESS = 0
        ERROR_INCORRECT_HEADER = 1
        ERROR_CHECKSUM_FAIL = 2
        ERROR_UNEXPECTED_RESPONSE = 3
        ERROR_INSUFFICIENT_ARRAY_SIZE = 4
        ERROR_CHECKSUM_MISMATCH = 5
        ERROR_SET_VALUE_MISMATCH = 6
        ERROR_VALUE_OUT_OF_BOUNDS = 7
        
    class Event_config(Enum):
        EVENT_OVERCUR_TST = 0
        EVENT_OVERPOW_TST = 1
        EVENT_VSAG_TST = 2
        EVENT_VSUR_TST = 3
        EVENT_OVERCUR_LA = 4
        EVENT_OVERPOW_LA = 5
        EVENT_VSAG_LA = 6
        EVENT_VSUR_LA = 7
        EVENT_VSAG_CL = 8
        EVENT_VSUR_CL = 9
        EVENT_OVERPOW_CL = 10
        EVENT_OVERCUR_CL = 11
        EVENT_MANUAL = 14
        EVENT_VSAG_PIN = 16
        EVENT_VSURGE_PIN = 17
        EVENT_OVERCUR_PIN = 18
        EVENT_OVERPOW_PIN = 19
        
    class System_status(Enum):
        SYSTEM_VSAG = 0
        SYSTEM_VSURGE = 1
        SYSTEM_OVERCUR = 2
        SYSTEM_OVERPOW = 3
        SYSTEM_SIGN_PA = 4
        SYSTEM_SIGN_PR = 5
        SYSTEM_EVENT = 10
        
    class calibration_config(Enum):
        CALIBRATION_CONFIG_4A = 0
        CALIBRATION_CONFIG_10A = 1 # 30 ohm burden resistor x2 
        CALIBRATION_CONFIG_15A = 2  # 20 ohm burden resistor x2
        CALIBRATION_CONFIG_15A_V2 = 3 # 20 ohm burden resistor x2, v2 board

    class __Response_code(Enum):
        RESPONSE_ACK = 0x06
        RESPONSE_NAK = 0x15
        RESPONSE_CSFAIL = 0x51

    class __Command_code(Enum):
        COMMAND_REGISTER_READ_N_BYTES = 0x4e
        COMMAND_REGISTER_WRITE_N_BYTES = 0x4d
        COMMAND_SET_ADDRESS_POINTER = 0x41
        COMMAND_SAVE_TO_FLASH = 0x53
        COMMAND_PAGE_READ_EEPROM = 0x42
        COMMAND_PAGE_WRITE_EEPROM = 0x50
        COMMAND_BULK_ERASE_EEPROM = 0x4f
        COMMAND_AUTO_CALIBRATE_GAIN = 0x5a
        COMMAND_AUTO_CALIBRATE_REACTIVE_GAIN = 0x7a
        COMMAND_AUTO_CALIBRATE_FREQUENCY = 0x76      

    ## There is a bug in current MCP39F511/521 where energy accumulation
    ## values are off if the energy accumulation interval is
    ## anything but 2. This applies the workaround for that problem.
    ## To be removed for chips that have the issue fixed.
    ## XXX : TODO
        
    def __init__(self, address=MCP39F521_I2CADDR, busnum=DEFAULT_BUSNUM):
        """Create an instance of the MCP39F521 device at the specified address on the
           specified I2C bus number."""
        self._address = address
        self._bus = SMBus(busnum)
        self._logger = logging.getLogger('DrWattson.UpbeatLabs_MCP39F521.Bus.{0}.Address.{1:#0X}'.format(busnum, address))
        self._energy_accum_correction_factor = 1
        (retVal, enabled) = self.isEnergyAccumulationEnabled()
        if (retVal == self.Error_code.SUCCESS.value and enabled):
            (retVal, accumIntervalReg) = self.readAccumulationIntervalRegister()
            self._energy_accum_correction_factor = (accumIntervalReg - 2);
                                    
    ## Get energy related data from the module
    ##
    ## Parameters:
    ## UpbeatLabs_MCP39F521_Data (output) - Metering data
    ##

            
    def readEnergyData(self):
        (retVal, buf) = self.__registerReadNBytes(0x00, 0x02, 28)
        data = UpbeatLabs_MCP39F521_Data()

        if (retVal == self.Error_code.SUCCESS.value):        
            data.systemStatus = (buf[3] << 8 | buf[2])
            data.systemVersion = (buf[5] << 8 | buf[4])
            data.voltageRMS = (buf[7] << 8 | buf[6] ) / 10.0
            data.lineFrequency = (buf[9] << 8 | buf [8]) / 1000.0
            data.analogInputVoltage = (buf[11] << 8 | buf[10]) /1023.0*3.3
            
            pfRaw = buf[13] << 8 | buf[12]
            f = ((pfRaw & 0x8000)>>15) * -1.0
  
            for ch in range(14, 3, -1):
                f += ((pfRaw & (1 << ch)) >> ch) * 1.0 / (1 << (15 - ch))

            data.powerFactor = f
            
            data.currentRMS = (buf[17] << 24 | buf[16] << 16 | buf[15] << 8 | buf[14]) / 10000.0
            data.activePower = (buf[21] << 24 | buf[20] << 16 | buf[19] << 8 | buf[18] ) / 100.0
            data.reactivePower = (buf[25] << 24 | buf[24] << 16 | buf[23] << 8 | buf[22] ) / 100.0
            data.apparentPower = (buf[29] << 24 | buf[28] << 16 | buf[27] << 8 | buf[26] ) / 100.0

        return (retVal, data)

    ## Get energy accumulator data from the module
    ##
    ## Parameters:
    ## UpbeatLabs_MCP39F521_AccumData (output) - accumulator data for energy
    ## Notes:
    ## On Arduino cannot read more than 32 bytes on I2C
    ## Let's just stick to that limit!
    ## Splitting out activeEnergyImport, activeEnergyExport and
    ## reactiveEnergyImport, reactiveEnergyExport into two calls
    ## as the total is 32+3 = 35 bytes otherwise.
    
    def readEnergyAccumData(self):
        (retVal, buf) = self.__registerReadNBytes(0x00, 0x1e, 16)
        data = UpbeatLabs_MCP39F521_AccumData()

        if (retVal == self.Error_code.SUCCESS.value):
            if (self._energy_accum_correction_factor == -1):
                data.activeEnergyImport =  (((buf[9]) << 56 |
                                            (buf[8]) << 48 |
                                            (buf[7]) << 40 |
                                            (buf[6]) << 32 |
                                            (buf[5]) << 24 |
                                            (buf[4]) << 16 |
                                            (buf[3]) << 8 |
                                            buf[2]) / 2 ) / 1000.0
                data.activeEnergyExport =  (((buf[17]) << 56 |
                                            (buf[16]) << 48 |
                                            (buf[15]) << 40 |
                                            (buf[14]) << 32 |
                                            (buf[13]) << 24 |
                                            (buf[12]) << 16 |
                                            (buf[11]) << 8 |
                                            buf[10]) / 2) / 1000.0
            else:
                data.activeEnergyImport =  (((buf[9]) << 56 |
                                            (buf[8]) << 48 |
                                            (buf[7]) << 40 |
                                            (buf[6]) << 32 |
                                            (buf[5]) << 24 |
                                            (buf[4]) << 16 |
                                            (buf[3]) << 8 |
                                            buf[2]) * ( 1 << self._energy_accum_correction_factor)) / 1000.0
                data.activeEnergyExport =  (((buf[17]) << 56 |
                                            (buf[16]) << 48 |
                                            (buf[15]) << 40 |
                                            (buf[14]) << 32 |
                                            (buf[13]) << 24 |
                                            (buf[12]) << 16 |
                                            (buf[11]) << 8 |
                                            buf[10]) * (1 << self._energy_accum_correction_factor)) / 1000.0

        time.sleep(0.05)
        (retVal, buf) = self.__registerReadNBytes(0x00, 0x2e, 16)

        if (retVal == self.Error_code.SUCCESS.value):
            if (self._energy_accum_correction_factor == -1):
                data.reactiveEnergyImport =  (((buf[9]) << 56 |
                                            (buf[8]) << 48 |
                                            (buf[7]) << 40 |
                                            (buf[6]) << 32 |
                                            (buf[5]) << 24 |
                                            (buf[4]) << 16 |
                                            (buf[3]) << 8 |
                                            buf[2]) / 2) / 1000.0
                data.reactiveEnergyExport =  (((buf[17]) << 56 |
                                            (buf[16]) << 48 |
                                            (buf[15]) << 40 |
                                            (buf[14]) << 32 |
                                            (buf[13]) << 24 |
                                            (buf[12]) << 16 |
                                            (buf[11]) << 8 |
                                            buf[10]) / 2) / 1000.0
            else:
                data.reactiveEnergyImport =  (((buf[9]) << 56 |
                                            (buf[8]) << 48 |
                                            (buf[7]) << 40 |
                                            (buf[6]) << 32 |
                                            (buf[5]) << 24 |
                                            (buf[4]) << 16 |
                                            (buf[3]) << 8 |
                                            buf[2]) * ( 1 << self._energy_accum_correction_factor)) / 1000.0
                data.reactiveEnergyExport =  (((buf[17]) << 56 |
                                            (buf[16]) << 48 |
                                            (buf[15]) << 40 |
                                            (buf[14]) << 32 |
                                            (buf[13]) << 24 |
                                            (buf[12]) << 16 |
                                            (buf[11]) << 8 |
                                            buf[10]) * (1 << self._energy_accum_correction_factor)) / 1000.0
             
        return (retVal, data)


    # Event control methods

    ## Reads the event configuration and returns the 32-bit bit map.
    ## Use the event_config enum to read bits of interest, without
    ## worrying about the bit position and structure of the
    ## event config register
    ##
    ## For example, bitRead(eventConfigRegisterValue, EVENT_VSAG_PIN)
    ## to see if event notification for VSAG events is turned on

    def readEventConfigRegister(self):
        (retVal, buf) = self.__registerReadNBytes(0x00, 0x7e, 4)
        configRegister = 0
        if (retVal == self.Error_code.SUCCESS.value): 
            configRegister = buf[5] << 24 | buf[4] << 16 | buf[3] << 8 | buf[2];
            
        return (retVal, configRegister)

    ## Set the event configuration register to the appropriate value
    ##
    ## First, read the existing register value. Then, set (or clear) appropriate
    ## bits using the event_config enum for assitance. Lastly, set the
    ## new value back in the register.
    ##
    ## For example, bitSet(eventConfigRegisterValue, EVENT_VSAG_PIN)
    ## to turn on the event notification for VSAG events
    ## or bitClear(eventConfigRegisterValue, EVENT_VSAG_PIN)
    
    def setEventConfigurationRegister(self, value):
        byteArray = []
        byteArray.append (value & 0xFF)
        byteArray.append ((value >> 8) & 0xFF)
        byteArray.append ((value >> 16) & 0xFF)
        byteArray.append ((value >> 24) & 0xFF)
        
        retVal = self.__registerWriteNBytes(0x00, 0x7e, 4, byteArray)
        if (retVal != self.Error_code.SUCCESS.value):
            return retVal

        (retVal, readArray) = self.__registerReadNBytes(0x00, 0x7e, 4)

        if (retVal == self.Error_code.SUCCESS.value):
            readValue = readArray[5] << 24 | readArray[4] << 16 | readArray[3] << 8 | readArray[2]

        if (readValue != value):
            return self.Error_code.ERROR_SET_VALUE_MISMATCH.value

        return self.Error_code.SUCCESS.value;

    ## Read the event flag limits that have been set for the various events.
    ## For example, the voltage sag limit sets the voltage value below which
    ## the VSAG event is triggered
    ##
    ## See UpbeatLabs_MCP39F521_EventFlagLimits for more information about
    ## various limits

    def readEventFlagLimitRegisters(self):
        (retVal, buf) = self.__registerReadNBytes(0x00, 0xA0, 12)
        data = UpbeatLabs_MCP39F521_EventFlagLimits()

        if (retVal == self.Error_code.SUCCESS.value):        
            data.voltageSagLimit = (buf[3] << 8 | buf[2])
            data.voltageSurgeLimit = (buf[5] << 8 | buf[4])
            data.overCurrentLimit = (buf[9] << 24 | buf[8] << 16 |buf[7] << 8 | buf[6] ) 
            data.overPowerLimit = (buf[13] << 24 | buf[12] << 16 |buf[11] << 8 | buf[10] ) 

        return (retVal, data)

    ## Write the event flag limits for the various events.
    ## For example, the voltage sag limit sets the voltage value below which
    ## the VSAG event is triggered
    ##
    ## See UpbeatLabs_MCP39F521_EventFlagLimits for more information about
    ## various limits
        
    def writeEventFlagLimitRegisters(self, input):
        byteArray = []
        byteArray.append(input.voltageSagLimit & 0xFF)
        byteArray.append((input.voltageSagLimit >> 8) & 0xFF)
        
        byteArray.append(input.voltageSurgeLimit & 0xFF)
        byteArray.append((input.voltageSurgeLimit >> 8) & 0xFF)

        byteArray.append(input.overCurrentLimit & 0xFF)
        byteArray.append((input.overCurrentLimit >> 8) & 0xFF)
        byteArray.append((input.overCurrentLimit >> 16) & 0xFF)
        byteArray.append((input.overCurrentLimit >> 24) & 0xFF)
        
        byteArray.append(input.overPowerLimit & 0xFF)
        byteArray.append((input.overPowerLimit >> 8) & 0xFF)
        byteArray.append((input.overPowerLimit >> 16) & 0xFF)
        byteArray.append((input.overPowerLimit >> 24) & 0xFF)

        retVal = self.__registerWriteNBytes(0x00, 0xA0, 12, byteArray)

        if (retVal != self.Error_code.SUCCESS.value):
            return retVal

        (retVal, eventFlagLimitsData) = self.readEventFlagLimitRegisters()
        if (retVal == self.Error_code.SUCCESS.value):
              ## Verify read values with input values
              if (eventFlagLimitsData.voltageSagLimit != input.voltageSagLimit or
                  eventFlagLimitsData.voltageSurgeLimit != input.voltageSurgeLimit or
                  eventFlagLimitsData.overCurrentLimit != input.overCurrentLimit or
                  eventFlagLimitsData.overPowerLimit != input.overPowerLimit):
                    return self.Error_code.ERROR_SET_VALUE_MISMATCH.value

        return retVal
      
    # EEPROM methods
    
    ## Bulk erase all pages of the EEPROM memory

    def bulkEraseEEPROM(self):
        return self.__issueAckNackCommand(self.__Command_code.COMMAND_BULK_ERASE_EEPROM.value)
    
    def pageReadEEPROM(self, pageNum):
        """Implementation of pageReadEEPROM """
        data = [0xa5, 0x05, self.__Command_code.COMMAND_PAGE_READ_EEPROM.value, pageNum]
        checksum = 0
        for x in data:
            checksum += x
        data.append(checksum % 256)
        
        write = i2c_msg.write(self._address, data)
        self._bus.i2c_rdwr(write)

        time.sleep(0.05)

        ##
        ## Read the specified length of data - ACK, Num Bytes, EEPROM Page Data, Checksum
        ## -> 1 + 1 + 16 + 1 = 19 bytes of data
        ##
        read = i2c_msg.read(self._address, 19)
        self._bus.i2c_rdwr(read)

        buf = []
        buf.extend(read)

        return (self.__checkHeaderAndChecksum(16, buf), buf[2:-1])
  
    def pageWriteEEPROM(self, pageNum, byteArray):
        """Implementation of pageWriteEEPROM """
        if (len(byteArray) != 16):
            return self.Error_code.ERROR_INSUFFICIENT_ARRAY_SIZE.value
        
        data = [0xa5, 21, self.__Command_code.COMMAND_PAGE_WRITE_EEPROM.value, pageNum]

        # Data here...
        data.extend(byteArray)
        
        checksum = 0
        for x in data:
            checksum += x
        data.append(checksum % 256)

        write = i2c_msg.write(self._address, data)
        self._bus.i2c_rdwr(write)

        time.sleep(0.05)

        header = self._bus.read_byte(self._address)
        self._logger.debug(header)

        return self.__checkHeader(header) 


    # Energy Accumulation methods


    ## This method is used to turn on/off energy accumulation.
    ## When it is turned on, the data read from the module
    ## in UpbeatLabs_MCP39F521_AccumData represents the
    ## accumulated energy data over the no load threshold
    ## (defaults to 1w). Therefore any energy over 1w
    ## gets accumulated over time.

    ## There is a bug in current MCP39F511/521 where energy accumulation
    ## values are off if the energy accumulation interval is
    ## anything but 2. This applies the workaround for that problem.
    ## To be removed for chips that have the issue fixed.
    
    def enableEnergyAccumulation(self, enable):
        ## First, note the accumulation interval. If it is anything
        ## other than the default (2), note the correction
        ## factor that has to be applied to the energy
        ## accumulation.
        (retVal, accumIntervalReg) = self.readAccumulationIntervalRegister()

        self._energy_accum_correction_factor = (accumIntervalReg - 2);

        byteArray = [enable, 0]

        ## write register
        retVal = self.__registerWriteNBytes(0x00, 0xDC, 2, byteArray);
 
        return retVal
    
    def isEnergyAccumulationEnabled(self):
        (retVal, readArray) = self.__registerReadNBytes(0x00, 0xDC, 5)
        enabled = False
        if (retVal == self.Error_code.SUCCESS.value):
            enabled = readArray[2];

        return (retVal, enabled)

    # <----   End Energy Accumulation methods
    

    # START --- WARNING!!! WARNING!!! WARNING!!!
    # Advanced methods for calibration, etc
    # WARNING!!!! Use with extreme caution! These can render your Dr. Wattson
    # uncalibrated. Only use if you know what you are doing!

    ## Read the contents of the calibration registers
    ## Results returned in UpbeatLabs_MCP39F521_CalibrationData object
  
    def readCalibrationRegisters(self):
        (retVal, buf) = self.__registerReadNBytes(0x00, 0x5e, 28)
        data = UpbeatLabs_MCP39F521_CalibrationData()

        if (retVal == self.Error_code.SUCCESS.value):        
            data.calibrationRegisterDelimiter = (buf[3] << 8 | buf[2])
            data.gainCurrentRMS = (buf[5] << 8 | buf[4])
            data.gainVoltageRMS = (buf[7] << 8 | buf[6] )
            data.gainActivePower = (buf[9] << 8 | buf [8])
            data.gainReactivePower = (buf[11] << 8 | buf[10])
            data.offsetCurrentRMS = (buf[15] << 24 | buf[14] << 16 | buf[13] << 8 | buf[12])
            data.offsetActivePower = (buf[19] << 24 | buf[18] << 16 | buf[17] << 8 | buf[16])
            data.offsetReactivePower = (buf[23] << 24 | buf[22] << 16 | buf[21] << 8 | buf[20])
            data.dcOffsetCurrent = (buf[25] << 8 | buf[24] )
            data.phaseCompensation = (buf[27] << 8 | buf[26] )
            data.apparentPowerDivisor = (buf[29] << 8 | buf[28] )

        return (retVal, data)

    ## This method writes the current, voltage, active power and reactive power gains directly to
    ## the MCP39F521 registers. Use this if you know what the appropriate gains are to be for 
    ## your particular metering range and design. Typically, these are not to be changed unless 
    ## you are performing your own calibration, and even so, it is better to use the
    ## auto-calibration methods instead. This is one big gun to shoot yourself, be warned!
  
    def writeGains(self, gainCurrentRMS, gainVoltageRMS,
                       gainActivePower, gainReactivePower):

        byteArray = []
        byteArray.append (gainCurrentRMS & 0xFF)
        byteArray.append ( (gainCurrentRMS >> 8) & 0xFF)

        byteArray.append ( gainVoltageRMS & 0xFF)
        byteArray.append ( (gainVoltageRMS >> 8) & 0xFF)

        byteArray.append ( gainActivePower & 0xFF)
        byteArray.append ( (gainActivePower >> 8) & 0xFF)

        byteArray.append ( gainReactivePower & 0xFF)
        byteArray.append ( (gainReactivePower >> 8) & 0xFF)
        
        retVal = self.__registerWriteNBytes(0x00, 0x60, 8, byteArray)
           
        return retVal

    ## Read the system config register, which is a 32-bit bit map.
    ## The system config register is used to set setting like
    ## PGA gains for current and voltage channels, etc
    ## You will typically not be changing these unless you are
    ## performing a calibration. 
    
    def readSystemConfigRegister(self):
        (retVal, buf) = self.__registerReadNBytes(0x00, 0x7a, 4)
        value = 0
        if (retVal == self.Error_code.SUCCESS.value):
            value = buf[5] << 24 | buf[4] << 16 | buf[3] << 8 | buf[2]
        return (retVal, value)


    ## Set the system config register, which is a 32-bit bit map.
    ## The system config register is used to set setting like
    ## PGA gains for current and voltage channels, etc
    ## You will typically not be changing these unless you are
    ## performing a calibration. Do not use unless you know what
    ## you are doing! This is one big gun to shoot yourself, be warned!
    
    def setSystemConfigurationRegister(self, value):
        retVal = 0;
        byteArray = [0]*4;
        byteArray[0] = value & 0xFF;
        byteArray[1] = (value >> 8) & 0xFF;
        byteArray[2] = (value >> 16) & 0xFF;
        byteArray[3] = (value >> 24) & 0xFF;
        # print byteArray
        
        retVal = self.__registerWriteNBytes(0x00, 0x7a, 4, byteArray);
        if (retVal != self.Error_code.SUCCESS.value):
            return retVal;
        
        time.sleep(0.05)
            
        (retVal, readArray) = self.__registerReadNBytes(0x00, 0x7a, 4);
        readValue = ((readArray[5]) << 24 | (readArray[4]) << 16 |
                         (readArray[3]) << 8 | readArray[2]);
          
        if (readValue != value):
            return self.Error_code.ERROR_SET_VALUE_MISMATCH.value;
        return self.Error_code.SUCCESS.value;

    ## Read the accumlation interval register, which represents N in 2^N
    ## number of line cycles to be used for a single computation.
    ## You will not be modifying this unless you are performing a
    ## calibration. 
    
    def readAccumulationIntervalRegister(self):
        (retVal, buf) = self.__registerReadNBytes(0x00, 0x9e, 2)
        value = 0
        if (retVal == self.Error_code.SUCCESS.value):
            value = buf[3] << 8 | buf[2]
        return (retVal, value)        

    ## Set the accumlation interval register, which represents N in 2^N
    ## number of line cycles to be used for a single computation.
    ## You will not be modifying this unless you are performing a
    ## calibration. Use with caution!!
    
    def setAccumulationIntervalRegister(self, value):
        retVal = 0;
        byteArray = [0]*2;
        byteArray[0] = value & 0xFF;
        byteArray[1] = (value >> 8) & 0xFF;
        
        retVal = self.__registerWriteNBytes(0x00, 0x9e, 2, byteArray);
        if (retVal != self.Error_code.SUCCESS.value):
            return retVal;
        
        time.sleep(0.05)
            
        (retVal, readArray) = self.__registerReadNBytes(0x00, 0x9e, 2);
        readValue = ((readArray[3]) << 8 | readArray[2]);
          
        if (readValue != value):
            return self.Error_code.ERROR_SET_VALUE_MISMATCH.value
        return self.Error_code.SUCCESS.value;

    ## Read the design config registers into the UpbeatLabs_MCP39F521_DesignConfigData struct.
    ## See class for more details. These are used to set the appropriate calibration values for
    ## calibrating your module.
    
    def readDesignConfigurationRegisters(self):
        (retVal, buf) = self.__registerReadNBytes(0x00, 0x82, 20)
        data = UpbeatLabs_MCP39F521_DesignConfigData()

        if (retVal == self.Error_code.SUCCESS.value):        
            data.rangeVoltage = buf[2]
            data.rangeCurrent = buf[3]
            data.rangePower = buf[4]
            data.rangeUnimplemented = buf[5]
            data.calibrationCurrent = (buf[9] << 24 | buf[8] << 16 | buf[7] << 8 | buf[6])
            data.calibrationVoltage = ((buf[11] << 8) | buf[10])
            data.calibrationPowerActive = (buf[15] << 24 | buf[14] << 16 | buf[13] << 8 | buf[12])
            data.calibrationPowerReactive = (buf[19] << 24 | buf[18] << 16 | buf[17] << 8 | buf[16])
            data.lineFrequencyRef = ((buf[21] << 8) | buf[20])

        return (retVal, data)        

    ## Write the design config registers. See UpbeatLabs_MCP39F521_DesignConfigData
    ## struct for more details. These are used to set the appropriate calibration values for
    ## calibrating your module. Use this method only if you know what you are doing!
    ## This is one big gun to shoot yourself, be warned!
    
    def writeDesignConfigRegisters(self, data):
        byteArray = []*20
        ## range
        byteArray[0] = data.rangeVoltage;
        byteArray[1] = data.rangeCurrent;
        byteArray[2] = data.rangePower;
        byteArray[3] = data.rangeUnimplemented;

        ## calibration current
        byteArray[4] = data.calibrationCurrent & 0xFF;
        byteArray[5] = (data.calibrationCurrent >> 8) & 0xFF;
        byteArray[6] = (data.calibrationCurrent >> 16) & 0xFF;
        byteArray[7] = (data.calibrationCurrent >> 24) & 0xFF;
        
        ## calibration voltage
        byteArray[8] = data.calibrationVoltage & 0xFF;
        byteArray[9] = (data.calibrationVoltage >> 8) & 0xFF;

        ## calibration power active
        byteArray[10] = data.calibrationPowerActive & 0xFF;
        byteArray[11] = (data.calibrationPowerActive >> 8) & 0xFF;
        byteArray[12] = (data.calibrationPowerActive >> 16) & 0xFF;
        byteArray[13] = (data.calibrationPowerActive >> 24) & 0xFF;

        ## calibration power reactive
        byteArray[14] = data.calibrationPowerReactive & 0xFF;
        byteArray[15] = (data.calibrationPowerReactive >> 8) & 0xFF;
        byteArray[16] = (data.calibrationPowerReactive >> 16) & 0xFF;
        byteArray[17] = (data.calibrationPowerReactive >> 24) & 0xFF;
        
        ## line frequency ref
        byteArray[18] = data.lineFrequencyRef & 0xFF;
        byteArray[19] = (data.lineFrequencyRef >> 8) & 0xFF;
        
        retVal = self.__registerWriteNBytes(0x00, 0x82, 20, byteArray)
        if (retVal != self.Error_code.SUCCESS.value):
            return retVal

        time.sleep(0.05)

        ## Read the values to verify write

        (retVal, designConfigData) = self.readDesignConfigurationRegisters();

        if (retVal != self.Error_code.SUCCESS.value):
            return retVal

        ## Verify read values with input values
        if (designConfigData.rangeVoltage != data.rangeVoltage or
            designConfigData.rangeCurrent != data.rangeCurrent or
            designConfigData.rangePower != data.rangePower or
            designConfigData.calibrationCurrent != data.calibrationCurrent or
            designConfigData.calibrationVoltage != data.calibrationVoltage or
            designConfigData.calibrationPowerActive != data.calibrationPowerActive or
            designConfigData.calibrationPowerReactive != data.calibrationPowerReactive or
            designConfigData.lineFrequencyRef != data.lineFrequencyRef): 
            return self.Error_code.ERROR_SET_VALUE_MISMATCH.value

        return self.Error_code.SUCCESS.value;

    ## Write the phase compensation register. This will not be required unless
    ## you are manually writing calibration values yourself. Use with caution!
    
    def writePhaseCompensation(self, phaseCompensation):

        byteArray = []*2
        ## Calibrating phase
        byteArray[0] = phaseCompensation;
        byteArray[1] = 0;
        
        retVal = self.__registerWriteNBytes(0x00, 0x76, 2, byteArray)
           
        return retVal

    ## Read and set the ambient reference temperature when
    ## calibrating. This is used during calibration as one
    ## of the steps. Use with caution!
    
    def readAndSetTemperature(self):
        (retVal, byteArray) = __registerReadNBytes(0x00, 0x0a, 2);

        if (retVal != self.Error_code.SUCCESS.value):
            return retVal

        bytesWrite = []*2
        bytesWrite[0] = byteArray[2];
        bytesWrite[1] = byteArray[3];

        retVal = self.__registerWriteNBytes(0x00, 0xcc, 2, bytesWrite);

        return retVal

    ## Invoke the "autoCalibrate Gain" command. Prior to this,
    ## other requisite steps need to be taken like setting
    ## the design config registers with the appropriate
    ## calibration values. Use only if you know what you are
    ## doing! This is one big gun to shoot yourself, be warned!      
    
    def autoCalibrateGain(self):
        return self.__issueAckNackCommand(self.__Command_code.COMMAND_AUTO_CALIBRATE_GAIN.value)


    ## Invoke the "autoCalibrate Reactive Gain" command. Prior to this,
    ## other requisite steps need to be taken like setting
    ## the design config registers with the appropriate
    ## calibration values, and auto calibrating gain.
    ## Use only if you know what you are doing!
    ## This is one big gun to shoot yourself, be warned!
    
    def autoCalibrateReactiveGain(self):
        return self.__issueAckNackCommand(self.__Command_code.COMMAND_AUTO_CALIBRATE_REACTIVE_GAIN.value)
    
    ## Invoke the "autoCalibrate Line Frequency" command. Prior to this,
    ## other requisite calibration steps need to be taken like setting
    ## the appropriate design config registers. 
    ## Use only if you know what you are doing!
    ## This is one big gun to shoot yourself, be warned!    
    
    def autoCalibrateFrequency(self):
        return self.__issueAckNackCommand(self.__Command_code.COMMAND_AUTO_CALIBRATE_FREQUENCY.value)

    ## This method is used to calibrate the phase compensation
    ## when calibrating the module, as one of the steps during
    ## system calibration. Use only if you know what you are doing!
    ## This is one big gun to shoot yourself, be warned!
    
    def calibratePhase(self, pfExp):
        (retVal, byteArray) = self.__registerReadNBytes(0x00, 0x0c, 2)

        if (retVal != self.Error_code.SUCCESS.value):
            return retVal

        pfRaw = buf[13] << 8 | buf[12]
        f = ((pfRaw & 0x8000)>>15) * -1.0
    
        for ch in range(14, 3, -1):
            f += ((pfRaw & (1 << ch)) >> ch) * 1.0 / (1 << (15 - ch))
        
        pfMeasured = f;

        angleMeasured = acos(pfMeasured);
        angleExp = acos(pfExp);
        angleMeasuredDeg = angleMeasured * 180.0/3.14159;
        angleExpDeg = angleExp * 180.0/3.14159;

        phi = (angleMeasuredDeg - angleExpDeg) * 40.0;
            
        (retVal, byteArray) = self.__registerReadNBytes(0x00, 0x76, 2)

        if (retVal != self.Error_code.SUCCESS.value):
            return retVal

        # phase compensation is stored as an 8-bit 2's complement number
        # (in a 16 bit register)
        pcRaw = byteArray[2]
        if pcRaw > 127:
            pcRaw = pcRaw - 256
        phaseComp = pcRaw

        phaseCompNew = phaseComp + phi;

        # New value has to be between 127 and -128 and has to be converted
        # back to an 8 bit integer for transmission
        if (phaseCompNew > 127 or phaseCompNew < -128):
            retVal = self.Error_code.ERROR_VALUE_OUT_OF_BOUNDS.value
        else:
            ## Calibrating phase
            bytes = [0]*2
            # converting back to 8 bit unsigned integer representation of
            # two's complement value
            bytes[0] = phaseCompNew if (phaseCompNew >= 0) else (256+phaseCompNew)
            bytes[1] = 0;
            
            retVal = self.__registerWriteNBytes(0x00, 0x76, 2, bytes)
            
        return retVal
    
            
    ## This method saves the contents of all calibration
    ## and configuration registers to flash. Use with caution!
    
    
    def saveToFlash(self):
        return self.__issueAckNackCommand(self.__Command_code.COMMAND_SAVE_TO_FLASH.value)

    # This will revert the MCP39F521 to its factory settings and
    # remove any calibration data. Use with extreme caution!!!!    

    def factoryReset(self):
        byteArray = [0]*2
        byteArray[0] = 0xa5;
        byteArray[1] = 0xa5;

        retVal = self.__registerWriteNBytes(0x00, 0x5e, 2, byteArray)

        if (retVal != self.Error_code.SUCCESS.value):
            return retVal

        retVal = self.saveToFlash();

        return retVal
  
    ## This method will reset the calibration values to Dr. Wattson
    
    def resetCalibration(self, cc = calibration_config.CALIBRATION_CONFIG_15A_V2.value):
        global calibConfig
        retVal = self.Error_code.SUCCESS.value

        retVal = self.setSystemConfigurationRegister(calibConfig[cc].systemConfig) # Channel 1 Gain 4, Channel 0 Gain 1
        if (retVal != self.Error_code.SUCCESS.value):
            return retVal

        retVal = self.setAccumulationIntervalRegister(calibConfig[cc].accumInt) # Accumulation interval 5
        if (retVal != self.Error_code.SUCCESS.value):
            return retVal

        ## We need to apply correction factor where accumulation interval is not 2;
        if (calibConfig[cc].accumInt > 2):
              self._energy_accum_correction_factor = (calibConfig[cc].accumInt - 2)

        
        retVal = self.writeDesignConfigRegisters(calibConfig[cc].designConfigData);
        if (retVal != self.Error_code.SUCCESS.value):
            return retVal
        
        retVal = self.writeGains(calibConfig[cc].gainCurrentRMS, calibConfig[cc].gainVoltageRMS, calibConfig[cc].gainActivePower, calibConfig[cc].gainReactivePower);
        if (retVal != self.Error_code.SUCCESS.value):
            return retVal;
        
        retVal = self.writePhaseCompensation(calibConfig[cc].phaseCompensation)
        if (retVal != self.Error_code.SUCCESS.value):
            return retVal;

        retVal = self.saveToFlash()
        if (retVal != self.Error_code.SUCCESS.value):
            return retVal;
        
        return self.Error_code.SUCCESS.value;

        

    # END --- WARNING!!! WARNING!!! WARNING!!!


    ## Bit manipulation convenience methods

    # Check to see if the kth bit is set in value n
    # (where k starts with 0 for the least significant bit
    def bitRead(self, n, k):
        return n & (1 << k)

    # Set the kth bit in value n
    # (where k starts with 0 for the least significant bit
    def bitSet(self, n, k):
        return n | (1 << k)

    # Clear the kth bit in value n
    # (where k starts with 0 for the least significant bit
    def bitClear(self, n, k):
        return n ^ (1 << k)

    
    ## Private methods ---

    ## Read the contents of the registers starting with the starting address,
    ## up to the number of bytes specified. 
    
    def __registerReadNBytes(self, addressHigh, addressLow, numBytesToRead):
        """Implementation of RegisterReadNBytes """
        data = [0xa5, 0x08, self.__Command_code.COMMAND_SET_ADDRESS_POINTER.value, addressHigh, addressLow, self.__Command_code.COMMAND_REGISTER_READ_N_BYTES.value,numBytesToRead]
        checksum = 0
        for x in data:
            checksum += x
        # Add checksum at the end    
        data.append( checksum % 256 )

        write = i2c_msg.write(self._address, data)
        self._bus.i2c_rdwr(write)

        time.sleep(0.05)
        
        read = i2c_msg.read(self._address, numBytesToRead + 3)
        self._bus.i2c_rdwr(read)
            
        buf = []
        buf.extend(read)
        # print buf

        return (self.__checkHeaderAndChecksum(numBytesToRead, buf), buf)
    
    ## Write to the registers, starting from the starting address the number of bytes
    ## specified in the byteArray
    
    def __registerWriteNBytes(self, addressHigh, addressLow, numBytes, byteArray):
        """Implementation of registerWriteNBytes """
        data = [0xa5, numBytes + 8, self.__Command_code.COMMAND_SET_ADDRESS_POINTER.value, addressHigh, addressLow, self.__Command_code.COMMAND_REGISTER_WRITE_N_BYTES.value,numBytes]
        ## data here
        data.extend(byteArray)
        # print data

        ## compute and fill checksum as last element
        checksum = 0
        for x in data:
            checksum += x
        data.append(checksum % 256)
        
        write = i2c_msg.write(self._address, data)
        self._bus.i2c_rdwr(write)

        time.sleep(0.05)

        header = self._bus.read_byte(self._address)
        self._logger.debug(header)

        return self.__checkHeader(header) 
    
  
    ## Some commands are issued and just return an ACK (or NAK)
    ## This method factors out those types of commands
    ## and takes in as argument the specified command to issue.
    
    def __issueAckNackCommand(self, command):
        """Implementation of issueAckNackCommand """
        # header, numBytes, command
        data = [0xa5, 0x04, command]
        checksum = 0 
        for x in data:
            checksum += x
        # Add checksum at the end    
        data.append (checksum % 256)

        write = i2c_msg.write(self._address, data)
        self._bus.i2c_rdwr(write)

        time.sleep(0.05)
        
        ## Read the ack
        header = self._bus.read_byte(self._address)
        self._logger.debug(header)
        
        return self.__checkHeader(header)
    

    ## Convenience method to check the header and the checksum for the returned data.
    ## If all is good, this method should return SUCCESS    

    def __checkHeaderAndChecksum(self, numBytesToRead, byteArray):
        """Implementation of checkHeaderAndChecksum """
        checksumTotal = 0
        header = byteArray[0]
        dataLen = byteArray[1]
        checksum = byteArray[numBytesToRead + 3 - 1]
        
        for i in range(0, numBytesToRead + 3 - 1):
            checksumTotal += byteArray[i]
            
        calculatedChecksum = checksumTotal % 256;
        error = self.Error_code.SUCCESS.value;

        error = self.__checkHeader(header);
  
        if (calculatedChecksum != checksum):
            error = self.Error_code.ERROR_CHECKSUM_MISMATCH.value
            
        return error;

    ## Convenience method to check the header of the response.
    ## If all is good, this will return SUCCESS
    
    def __checkHeader(self, header):
        """Implementation of checkHeader """
        error = self.Error_code.SUCCESS.value;
        if (header != self.__Response_code.RESPONSE_ACK.value):
            error = self.Error_code.ERROR_INCORRECT_HEADER.value
            
        if (header == self.__Response_code.RESPONSE_CSFAIL.value):
            error = self.Error_code.ERROR_CHECKSUM_FAIL.value
            
        return error
    
