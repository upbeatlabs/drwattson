/*************************************************** 
  This is a example sketch for Upbeat Labs Dr. Wattson Energy Monitoring Breakout
  --> https://www.tindie.com/products/UpbeatLabs/dr-wattson-energy-monitoring-board-2/

  This example demonstrates the use of EEPROM memory available on the MCP39F521. 
  There are 32 pages of memory of 16 bytes each (for a total of 512 bytes), that 
  can be read and updated. 

  In this example, we first do a bulk erase of all EEPROM memory, then read and print 
  the contents, then update it with our own, and read and print the contents again.

  The communication happens over I2C. 2 pins are required to interface. 
  There are 4 selectable I2C address possibilities per board (selectable
  via two solder jumpers (that select each pin to be high or low). Based 
  on this, there are 4 possible addresses:

  I2C address  SJ1   SJ2
  0x74         LOW   LOW
  0x75         LOW   HIGH
  0x76         HIGH  LOW
  0x77         HIGH  HIGH

  There are also 2 output pins - ZCD and EVENT that can be connected to
  interrupt pins 2 and 3. In this example, they are not used
 
  Written by Sridhar Rajagopal for Upbeat Labs LLC.
  BSD license. All text above must be included in any redistribution
 */
 
#include <Wire.h>
#include "UpbeatLabs_MCP39F521.h"

// Pin 13 has an LED connected on most Arduino boards.
// give it a name:
int led = 13;

UpbeatLabs_MCP39F521 wattson = UpbeatLabs_MCP39F521();

void setup() {                
  // initialize the digital pin as an output.
  pinMode(led, OUTPUT);     
  Serial.begin(9600);  //turn on serial communication
  Serial.println("Upbeat Labs Dr. Wattson EEPROM Example Sketch");
  Serial.println("*********************************************");
  
  wattson.begin(); // Pass in the appropriate address. Defaults to 0x74

  EEPROMBulkErase();
  EEPROMRead();
  EEPROMWrite();
  EEPROMRead();
}
 
void loop() {

}

void EEPROMBulkErase()
{
  int retVal = UpbeatLabs_MCP39F521::SUCCESS;
  Serial.println("Bulk Erase EEPROM");
  retVal = wattson.bulkEraseEEPROM();
    if (retVal != UpbeatLabs_MCP39F521::SUCCESS) {
      Serial.print("Error "); Serial.print(retVal);
      Serial.println(" with bulk erase EEPROM");
    }  
}

void EEPROMRead()
{
  uint8_t byteArray[16];
  int retVal = UpbeatLabs_MCP39F521::SUCCESS;

  Serial.println("Read EEPROM Pages");

  for (int j = 0; j < 32; j++) { 
    retVal = wattson.pageReadEEPROM(j, byteArray, 16);
    if (retVal != UpbeatLabs_MCP39F521::SUCCESS) {
      Serial.print("Error "); Serial.print(retVal);
      Serial.print(" reading from EEPROM page ");
      Serial.println(j);
    }
    for (int i = 0; i < 16; i++) {
      Serial.print(byteArray[i]); Serial.print(" ");
    }
    Serial.println();
  }
}

void EEPROMWrite()
{
  uint8_t byteArray[16] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15};
  int retVal = UpbeatLabs_MCP39F521::SUCCESS;

  Serial.println("Write EEPROM Pages");
  
  for (int i = 0; i < 32; i++) {
    retVal = wattson.pageWriteEEPROM(i, byteArray, 16);
    if (retVal != UpbeatLabs_MCP39F521::SUCCESS) {
      Serial.print("Error "); Serial.print(retVal);
      Serial.print(" writing to EEPROM page ");
      Serial.println(i);
    }
  }
}
