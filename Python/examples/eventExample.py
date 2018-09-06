# *************************************************** 
#   This is a example program for Upbeat Labs Dr. Wattson Energy Monitoring Breakout
#   --> https://www.tindie.com/products/UpbeatLabs/dr-wattson-energy-monitoring-board-2/

#   This example demonstrates the event capabilities of the MCP39F521 used in Dr. Wattson.
#   It can generate signals on the EVENT pin which can then be attached to an 
#   externally interruptable pin to get notifications of events of 
#   interest. Further details of which event occured, etc, can be obtained by querying
#   the module's system Status and processing the result.

#   In this example, we enable Voltage Sag, Voltage Surge, Over Current and Over Power
#   events, and also set the appropriate limits when these events will get generated. 
#   Voltage sag if voltage drops below 80v, Over current if current goes above 0.18 amps, 
#   and Over Power if active power goes above 16 watts. When the event of interest happens
#   you can see appropriate messages in the output. The messages continue as long as 
#   the event persists. 

#   To trigger the Voltage Sag event, you can turn off power to your input. 
#   To trigger Over Current and Over Power, you can turn on the load on your output. 
#   The limits were set to be above the current and active power consumption of a 14w
#   CFL bulb - you can set appropriate limits for your load of choice. 

#   To stop the Voltage Sag event, turn on the input power to restore voltage back. 
#   To stop the Over Current and Over Power events, simply turn off your load (once
#   input power has been restored). 

#   The communication happens over I2C. 2 pins are required to interface. 
#   There are 4 selectable I2C address possibilities per board (selectable
#   via two solder jumpers (that select each pin to be high or low). Based 
#   on this, there are 4 possible addresses:

#   I2C address  SJ1   SJ2
#   0x74         LOW   LOW
#   0x75         LOW   HIGH
#   0x76         HIGH  LOW
#   0x77         HIGH  HIGH

#   There are also 2 output pins - ZCD and EVENT that generate external
#   interrupts. In this example, ZCD is not used. EVENT is connected to
#   GPIO BMC pin 24 (physical pin 16). When EVENT pin is turned on/off
#   an interrupt is generated and invokes the event_handler, which
#   changes the state of the LED (on physical pin 12, BCM pin 18) to match the
#   event state
 
#   Written by Sridhar Rajagopal for Upbeat Labs LLC.
#   BSD license. All text above must be included in any redistribution
#  *

from __future__ import print_function
import signal
import time
import subprocess as sp
import RPi.GPIO as GPIO

import UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521 as UpbeatLabs_MCP39F521

wattson = UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521()

LED_PIN = 18
ZCD_PIN = 23
EVENT_PIN = 24



def main():
    initialize()
    setSystemConfig()
    
    while(True):
        tmp = sp.call('clear',shell=True)

        (retVal, data) = wattson.readEnergyData()
     
        if (retVal != UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521.Error_code.SUCCESS.value):
            print("Error reading energy data: {}".format(retVal))

        checkSystemStatus(data.systemStatus);
    
        time.sleep(1);

def initialize():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LED_PIN,GPIO.OUT)

    GPIO.setup(ZCD_PIN, GPIO.IN)
    GPIO.setup(EVENT_PIN, GPIO.IN)

    GPIO.add_event_detect(EVENT_PIN, GPIO.BOTH, event_handler)

def event_handler(pin):
    state = GPIO.input(pin)
    GPIO.output(LED_PIN, state)      

def setSystemConfig():
      (retVal, eventData) = wattson.readEventConfigRegister()

      print("eventConfigRegister is {}".format(eventData))

      (retVal, eventFlagLimits)  = wattson.readEventFlagLimitRegisters()

      print("voltageSagLimit = {0}, voltageSurgeLimit = {1}, overCurrentLimit = {2}, overPowerLimit = {3}".format(
            eventFlagLimits.voltageSagLimit, eventFlagLimits.voltageSurgeLimit, eventFlagLimits.overCurrentLimit, eventFlagLimits.overPowerLimit))

      eventFlagLimits.overCurrentLimit = 1800 # 0.18a
      eventFlagLimits.overPowerLimit = 1600 # 16w
      retVal = wattson.writeEventFlagLimitRegisters(eventFlagLimits);

      eventData = 0

      ## Map Voltage Sag Event to event pin
      eventData = bitSet(eventData, UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521.Event_config.EVENT_VSAG_PIN.value)
      ## Map Voltage Surge Event to event pin
      eventData = bitSet(eventData, UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521.Event_config.EVENT_VSURGE_PIN.value)
      ## Map Over Current Event to event pin
      eventData = bitSet(eventData, UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521.Event_config.EVENT_OVERCUR_PIN.value)
      ## Map Over Power Event to event pin
      eventData = bitSet(eventData, UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521.Event_config.EVENT_OVERPOW_PIN.value)
  
      print("Event Config Register set to {}".format(eventData));
      
      retVal = wattson.setEventConfigurationRegister(eventData);

def bitSet(value, bit):
    value |= (1 << (bit))
    return value

def bitRead(value, bit):
    return (((value) >> (bit)) & 0x01)

def bitClear(value, bit):
    value &= ~(1 << (bit))
    return value

def bitWrite(value, bit, bitValue):
    return bitSet(value, bit) if bitValue else bitClear(value, bit)


def checkSystemStatus(systemStatus):
    print("System Status value is {}".format(systemStatus))
    if (bitRead(systemStatus, UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521.System_status.SYSTEM_EVENT.value) == 1):
        print("event bit set") 
  
    if (bitRead(systemStatus, UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521.System_status.SYSTEM_VSAG.value) == 1):
        print("VSAG bit set") 
  
    if (bitRead(systemStatus, UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521.System_status.SYSTEM_VSURGE.value) == 1):
        print("VSURGE bit set") 
  

    if (bitRead(systemStatus, UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521.System_status.SYSTEM_OVERCUR.value) == 1):
        print("OVERCUR bit set") 
  

    if (bitRead(systemStatus, UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521.System_status.SYSTEM_OVERPOW.value) == 1):
        print("OVERPOW bit set") 
  
  
    if (bitRead(systemStatus, UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521.System_status.SYSTEM_SIGN_PA.value) == 1):
        print("SIGN_PA bit set") 
  

    if (bitRead(systemStatus, UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521.System_status.SYSTEM_SIGN_PR.value) == 1):
        print("SIGN_PR bit set") 
  

# gracefully exit without a big exception message if possible
def ctrl_c_handler(signal, frame):
    print('Goodbye!')
    exit(0)

signal.signal(signal.SIGINT, ctrl_c_handler)

if __name__ == '__main__':
    main()
