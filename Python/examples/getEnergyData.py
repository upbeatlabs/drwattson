#!/usr/bin/python

#*****************************************************************************
# This is a example program for Upbeat Labs Dr. Wattson Energy Monitoring Breakout
# --> https://www.tindie.com/products/UpbeatLabs/dr-wattson-energy-monitoring-board-2/

# This example demonstrates getting Energy Data from Dr. Wattson.

# The program starts to poll the module for Energy data and prints it out in a loop.

# Turn on the input power to see the voltage RMS, line frequency values 
# change to the appropriate values. 

# Turn on the load attached to your output to see current RMS, power factor, 
# active, reactive and apparent power values change. 

# The communication happens over I2C. 2 pins are required to interface. 
# There are 4 selectable I2C address possibilities per board (selectable
# via two solder jumpers SJ1 and SJ2 (that select each pin to be high or low).
# Based on this, there are 4 possible addresses:

# I2C address  SJ1   SJ2
# 0x74         LOW   LOW
# 0x75         LOW   HIGH
# 0x76         HIGH  LOW
# 0x77         HIGH  HIGH

# Written by Sridhar Rajagopal for Upbeat Labs LLC.
# BSD license. All text above must be included in any redistribution

import UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521 as UpbeatLabs_MCP39F521
import subprocess as sp

wattson = UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521()

while(1):
    tmp = sp.call('clear',shell=True)
    (ret, result) = wattson.readEnergyData()
    print "VoltageRMS = " + str(result.voltageRMS)
    print "CurrentRMS = " + str(result.currentRMS)
    print "LineFrequency = " + str(result.lineFrequency)
    print "PowerFactor = " + str(result.powerFactor)
    print "ActivePower = " + str(result.activePower)
    print "ReactivePower = " + str(result.reactivePower)
    print "ApparentPower = " + str(result.apparentPower)
    
