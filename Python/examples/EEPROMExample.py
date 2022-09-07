# *************************************************** 
#   This is a example program for Upbeat Labs Dr. Wattson Energy Monitoring Breakout
#   --> https://www.protostax.com/products/dr-wattson-energy-monitoring-board-v2/

#   This example demonstrates the use of EEPROM memory available on the MCP39F521. 
#   There are 32 pages of memory of 16 bytes each (for a total of 512 bytes), that 
#   can be read and updated. 

#   In this example, we first read the existing contents, do a bulk erase of all
#   EEPROM memory, then read and print the contents, then update it with our own,
#   and read and print the contents again.

#   The communication happens over I2C. 2 pins are required to interface. 
#   There are 4 selectable I2C address possibilities per board (selectable
#   via two solder jumpers (that select each pin to be high or low). Based 
#   on this, there are 4 possible addresses:

#   I2C address  SJ1   SJ2
#   0x74         LOW   LOW
#   0x75         LOW   HIGH
#   0x76         HIGH  LOW
#   0x77         HIGH  HIGH

#   There are also 2 output pins - ZCD and EVENT that can be used for
#   external interrupts on Zero Cross Detection and certain
#   configured events. In this example, they are not used
 
#   Written by Sridhar Rajagopal for Upbeat Labs LLC.
#   BSD license. All text above must be included in any redistribution
# *

from __future__ import print_function
import signal

import UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521 as UpbeatLabs_MCP39F521

wattson = UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521()

def main():
    EEPROMRead()
    EEPROMBulkErase()
    EEPROMRead()
    EEPROMWrite()
    EEPROMRead()


def EEPROMBulkErase():
    print("Bulk Erase EEPROM")
    retVal = wattson.bulkEraseEEPROM()
      
    if (retVal != UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521.Error_code.SUCCESS.value):
        print("Error {} with bulk erase EEPROM".format(retVal))
        
    return

def EEPROMRead():
    print("Read EEPROM Pages");

    for j in range(0, 32):
        (retVal, byteArray) = wattson.pageReadEEPROM(j)
        if (retVal != UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521.Error_code.SUCCESS.value):
            print("Error {} reading from EEPROM page {}".format(retVal, j))
            
        for i in range(0, 16):
            print(byteArray[i], end='')
        print()
    
    return
    
def EEPROMWrite():
    print("Write EEPROM Pages");

    byteArray = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15];
  
    for i in range(0, 32):
        retVal = wattson.pageWriteEEPROM(i, byteArray)
        
    if (retVal != UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521.Error_code.SUCCESS.value):
        print("Error {} writing to EEPROM page {}".format(retVal, j))

    return

# gracefully exit without a big exception message if possible
def ctrl_c_handler(signal, frame):
    print('Goodbye!')
    exit(0)

signal.signal(signal.SIGINT, ctrl_c_handler)

if __name__ == '__main__':
    main()
