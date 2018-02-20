/*************************************************** 
  This is a example sketch for Upbeat Labs Dr. Wattson Energy Monitoring Breakout
  --> https://www.tindie.com/products/UpbeatLabs/dr-wattson-energy-monitoring-board-2/

  This example demonstrates getting Energy Data from Dr. Wattson.

  Additionally, it also demonstrates getting ZCD (Zero Cross Detection) interrupts. 
  These can be used to trigger a triac, for example, to act as a light dimmer. 

  The sketch starts to poll the module for Energy data and prints it out. 
  For ease of seeing the values, use a program like screen to display 
  the Serial output. The serial writes the characters necessary to 
  clear the screen on a regular terminal, which means that the serial
  output will stay in place and just update over time. 

  Turn on the input power to see the voltage RMS, line frequency values 
  change to the appropriate values. 

  Turn on the load attached to your output to see current RMS, power factor, 
  active, reactive and apparent power values change. 

  Note that the LED 13 on your Arduino will flash about 40 times a second, 
  in response to the ZCD input that is scaled down (from the 120 times a second
  that the interrupt will get called in response to CHANGEing values of the pin - 
  60Hz will change from high to low and low to high twice per cycle, hence 120
  times a second). Change the SLOW_DOWN_FACTOR to a higher value to slow down 
  the LED pulse even further. See comments below for more information. 

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
  interrupt pins 2 and 3. In this example, ZCD is connected to pin 2's
  interrupt
 
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
  attachInterrupt(0, zcd, CHANGE);
  Serial.begin(9600);  //turn on serial communication
  Serial.println("Upbeat Labs Dr. Wattson Energy Data Example Sketch");
  Serial.println("**************************************************");
  
  wattson.begin(); // Pass in the appropriate address. Defaults to 0x74
}
 
void loop() {
  UpbeatLabs_MCP39F521_Data data;
  UpbeatLabs_MCP39F521_FormattedData fData;

  int readMCPretval = wattson.read(&data, NULL);
  if (readMCPretval == UpbeatLabs_MCP39F521::SUCCESS) {
    // Print stuff out
    Serial.write("\x1B" "c"); // Clear the screen on a regular terminal                               
    wattson.convertRawData(&data, &fData);
    printMCP39F521Data(&fData);
  } else {
    Serial.print("Error returned! "); Serial.println(readMCPretval);
  }

  delay(1000);               // wait for a second
}

// Interrupt service routine for ZCD

// Since the voltage crosses zero twice in a cycle,
// ZCD interrupt will be firing at 50 or 60 Hz * 2
// or at 100 to 120 times a second. 
// This example toggles the onboard LED 13 corresponding
// to Zero Cross Detection
// In order to make the interrupt firing more visible
// we use a SLOW_DOWN_FACTOR to reduce the frequency
// at which the LED toggles. A SLOW_DOWN_FACTOR of
// 3 means that at 60 Hz, we will toggle the LED
// 40 times a second (120/3). A SLOW_DOWN_FACTOR of 120 means that
// the LED will flash 120/120 = 1 times a second

#define SLOW_DOWN_FACTOR 3

void zcd() {
  static int state = HIGH;
  static int numInterrupts = 0;
  digitalWrite(led, state);
  numInterrupts++;
  numInterrupts = numInterrupts % SLOW_DOWN_FACTOR;
  if (numInterrupts == (SLOW_DOWN_FACTOR-1)) {
    state = !state;
  }
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
