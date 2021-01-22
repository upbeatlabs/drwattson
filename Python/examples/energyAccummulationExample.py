# *************************************************** 
#   This is a example program for Upbeat Labs Dr. Wattson Energy Monitoring Breakout
#   --> https://www.tindie.com/products/UpbeatLabs/dr-wattson-energy-monitoring-board-2/

#   This example demonstrates enabling energy accumulation on Dr. Wattson.

#   The program starts to poll the module for Energy data and prints it out in a loop.

#   Turn on the input power to see the voltage RMS, line frequency values 
#   change to the appropriate values. 

#   Turn on the load attached to your output to see current RMS, power factor, 
#   active, reactive and apparent power values change. Also see the
#   accumulated energy data increasing with time when the load is on.

#   The communication happens over I2C. 2 pins are required to interface. 
#   There are 4 selectable I2C address possibilities per board (selectable
#   via two solder jumpers (that select each pin to be high or low). Based 
#   on this, there are 4 possible addresses:

#   I2C address  SJ1   SJ2
#   0x74         LOW   LOW
#   0x75         LOW   HIGH
#   0x76         HIGH  LOW
#   0x77         HIGH  HIGH
 
#   Written by Sridhar Rajagopal for Upbeat Labs LLC.
#   BSD license. All text above must be included in any redistribution
#  *


import UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521 as UpbeatLabs_MCP39F521
import subprocess as sp
import signal
import time

wattson = UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521()

def main():
    initialize()

    while(True):
        tmp = sp.call('clear',shell=True)
        (ret, energyData) = wattson.readEnergyData()
        (ret, energyAccumData) = wattson.readEnergyAccumData()

        print "VoltageRMS = " + str(energyData.voltageRMS)
        print "CurrentRMS = " + str(energyData.currentRMS)
        print "LineFrequency = " + str(energyData.lineFrequency)
        print "PowerFactor = " + str(energyData.powerFactor)
        print "ActivePower = " + str(energyData.activePower)
        print "ReactivePower = " + str(energyData.reactivePower)
        print "ApparentPower = " + str(energyData.apparentPower)
        
        print "ActiveEnergyImport = " + str(energyAccumData.activeEnergyImport)
        print "ReactiveEnergyImport = " + str(energyAccumData.reactiveEnergyImport)
        print "ActiveEnergyExport = " + str(energyAccumData.activeEnergyExport)
        print "ReactiveEnergyExport = " + str(energyAccumData.reactiveEnergyExport)
        time.sleep(1)
 


def initialize():
    retVal, accumIntervalReg = wattson.readAccumulationIntervalRegister()
    print("Accumulation interval is {}".format(accumIntervalReg))

    time.sleep(1);

    ## Turn off any previous energy accumulation
    print("Turn off any previous accumulation")
    wattson.enableEnergyAccumulation(False)

    ## Wait for sometime for registers to reset before re-enabling them
    time.sleep(1);
  
    ## Turn on energy accumulation
    print("Re-enable accumulation");
    wattson.enableEnergyAccumulation(True)   


# gracefully exit without a big exception message if possible
def ctrl_c_handler(signal, frame):
    # Turn off energy accumulation that was turned on by this example
    wattson.enableEnergyAccumulation(False)
    print('Goodbye!')
    exit(0)

signal.signal(signal.SIGINT, ctrl_c_handler)

if __name__ == '__main__':
    main()
