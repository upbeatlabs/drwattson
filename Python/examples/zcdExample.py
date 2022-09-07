# *************************************************** 
#   This is a example program for Upbeat Labs Dr. Wattson Energy Monitoring Breakout
#   --> https://www.protostax.com/products/dr-wattson-energy-monitoring-board-v2/

#   This example demonstrates getting ZCD (Zero Cross Detection) interrupts. 
#   These can be used to trigger a triac, for example, to act as a light dimmer. 

#   Note that the LED_PIN on your RPi will flash about 1 time a second, 
#   in response to the ZCD input that is scaled down (from the 120 times a second
#   that the interrupt will get called in response to CHANGEing values of the pin - 
#   60Hz will change from high to low and low to high twice per cycle, hence 120
#   times a second). SLOW_DOWN_FACTOR of 60 means that the LED will toggle
#   twice a second - or in other words, it lights up every second!

#   The communication happens over I2C. 2 pins are required to interface. 
#   There are 4 selectable I2C address possibilities per board (selectable
#   via two solder jumpers (that select each pin to be high or low). Based 
#   on this, there are 4 possible addresses:

#   I2C address  SJ1   SJ2
#   0x74         LOW   LOW
#   0x75         LOW   HIGH
#   0x76         HIGH  LOW
#   0x77         HIGH  HIGH

#   There are 2 output pins - ZCD and EVENT that generate external
#   interrupts. In this example, ZCD is not is connected to 
#   GPIO BMC pin 23 (physical pin 16). When ZCD pin is turned on/off
#   an interrupt is generated and invokes the zcd_handler, which
#   toggles the state of the LED (on physical pin 22, BCM pin 25)
#   at the rate determined by the SLOW_DOWN_FACTOR. The EVENT pin is
#   not used in this example.
 
#   Written by Sridhar Rajagopal for Upbeat Labs LLC.
#   BSD license. All text above must be included in any redistribution
#  *

from __future__ import print_function
import sys
import signal
import time
import subprocess as sp
import RPi.GPIO as GPIO

import UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521 as UpbeatLabs_MCP39F521

wattson = UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521()

LED_PIN = 25
ZCD_PIN = 23
EVENT_PIN = 24

# Will cause LED to toggle twice a second, i.e. light up every second
SLOW_DOWN_FACTOR = 60 

# Thanks to the following for the static
# variable trick!
# https://stackoverflow.com/a/279586

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


def main():
    initialize()
    
    while(True):    
        time.sleep(1);

def initialize():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LED_PIN,GPIO.OUT)

    GPIO.setup(ZCD_PIN, GPIO.IN)

    GPIO.add_event_detect(ZCD_PIN, GPIO.BOTH, zcd_handler)

def cleanup():
    GPIO.remove_event_detect(ZCD_PIN)
    GPIO.output(LED_PIN, 0)
    GPIO.cleanup()

# Attach two "static" variables to the function to track state
# across calls
@static_vars(state=GPIO.HIGH, numInterrupts=0)
def zcd_handler(pin):

  GPIO.output(LED_PIN, zcd_handler.state);
  zcd_handler.numInterrupts += 1;
  zcd_handler.numInterrupts = zcd_handler.numInterrupts % SLOW_DOWN_FACTOR;
  if (zcd_handler.numInterrupts == (SLOW_DOWN_FACTOR-1)):
    zcd_handler.state = not zcd_handler.state


    

# gracefully exit without a big exception message if possible
def ctrl_c_handler(signal, frame):
    print("Goodbye!")
    cleanup()
    exit(0)


signal.signal(signal.SIGINT, ctrl_c_handler)

if __name__ == '__main__':
    main()
