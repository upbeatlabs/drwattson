# *************************************************** 
#   This is a example program for Upbeat Labs Dr. Wattson Energy Monitoring Breakout
#   --> https://www.protostax.com/products/dr-wattson-energy-monitoring-board-v2/

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

        print("VoltageRMS = {:5.2f}".format(energyData.voltageRMS))
        print("CurrentRMS = {:5.2f}".format(energyData.currentRMS))
        print("LineFrequency = {:5.2f}".format(energyData.lineFrequency))
        print("PowerFactor = {:5.2f}".format(energyData.powerFactor))
        print("ActivePower = {:5.2f}".format(energyData.activePower))
        print("ReactivePower = {:5.2f}".format(energyData.reactivePower))
        print("ApparentPower = {:5.2f}".format(energyData.apparentPower))
        print("")
        print("ActiveEnergyImport = {:5.2f}".format(energyAccumData.activeEnergyImport))
        print("ReactiveEnergyImport = {:5.2f}".format(energyAccumData.reactiveEnergyImport))
        print("ActiveEnergyExport = {:5.2f}".format(energyAccumData.activeEnergyExport))
        print("ReactiveEnergyExport = {:5.2f}".format(energyAccumData.reactiveEnergyExport))
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
