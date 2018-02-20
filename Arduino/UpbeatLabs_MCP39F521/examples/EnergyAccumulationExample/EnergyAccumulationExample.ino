/*************************************************** 
  This is a example sketch for Upbeat Labs Dr. Wattson Energy Monitoring Breakout
  --> https://www.tindie.com/products/UpbeatLabs/dr-wattson-energy-monitoring-board-2/

  This example demonstrates enabling energy accumulation on Dr. Wattson.

  The sketch starts to poll the module for Energy data and prints it out. 
  For ease of seeing the values, use a program like screen to display 
  the Serial output. The serial writes the characters necessary to 
  clear the screen on a regular terminal, which means that the serial
  output will stay in place and just update over time. 

  Turn on the input power to see the voltage RMS, line frequency values 
  change to the appropriate values. 

  Turn on the load attached to your output to see current RMS, power factor, 
  active, reactive and apparent power values change. Also see the
  accumulated energy data increasing with time when the load is on.

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
  interrupt pins 2 and 3. In this example, they are not used.
 
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
  Serial.println("Upbeat Labs Dr. Wattson Energy Data Accumulation Example Sketch");
  Serial.println("***************************************************************");
  
  wattson.begin(); // Pass in the appropriate address. Defaults to 0x74

  int accumIntervalReg; 

  wattson.readAccumulationIntervalRegister(&accumIntervalReg);

  Serial.print("Accumulation interval is "); Serial.println(accumIntervalReg);

  delay(100);

  // Turn off any previous energy accumulation
  Serial.println("Turn off any previous accumulation");
  wattson.enableEnergyAccumulation(false);

  // Wait for sometime for registers to reset before re-enabling them
  delay(1000);
  
  // Turn on energy accumulation
  Serial.println("Re-enable accumulation");
  wattson.enableEnergyAccumulation(true);
}
 
void loop() {
  UpbeatLabs_MCP39F521_Data data;
  UpbeatLabs_MCP39F521_FormattedData fData;

  UpbeatLabs_MCP39F521_AccumData aData;
  UpbeatLabs_MCP39F521_FormattedAccumData afData;

  int readMCPretval = wattson.read(&data, &aData);
  if (readMCPretval == UpbeatLabs_MCP39F521::SUCCESS) {
    // Print stuff out
    Serial.write("\x1B" "c"); // Clear the screen on a regular terminal                               
    wattson.convertRawData(&data, &fData);
    wattson.convertRawAccumData(&aData, &afData);
    printMCP39F521Data(&fData);
    printMCP39F521AccumData(&afData);
  } else {
   Serial.println("Error!"); 
  }

  delay(1000);               // wait for a second
}


void printMCP39F521Data(UpbeatLabs_MCP39F521_FormattedData *data)
{
  Serial.print(F("Voltage = ")); Serial.println(data->voltageRMS, 4);
  Serial.print(F("Current = ")); Serial.println(data->currentRMS, 4);
  Serial.print(F("Line Frequency = ")); Serial.println(data->lineFrequency, 4);
  Serial.print("Analog Input Voltage = "); Serial.println(data->analogInputVoltage, 4);
  Serial.print(F("Power Factor = ")); Serial.println(data->powerFactor, 4);
  Serial.print(F("Active Power = ")); Serial.println(data->activePower, 4);
  Serial.print(F("Reactive Power = ")); Serial.println(data->reactivePower, 4);
  Serial.print(F("Apparent Power = ")); Serial.println(data->apparentPower, 4);
}

void printMCP39F521AccumData(UpbeatLabs_MCP39F521_FormattedAccumData *data)
{
  Serial.print("Active Energy Import = "); Serial.println(data->activeEnergyImport, 4);
  Serial.print("Active Energy Export = "); Serial.println(data->activeEnergyExport, 4);
  Serial.print("Reactive Energy Import = "); Serial.println(data->reactiveEnergyImport, 4);
  Serial.print("Reactive Energy Export = "); Serial.println(data->reactiveEnergyExport, 4);
}
