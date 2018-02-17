/*************************************************** 
  This is a example sketch for Upbeat Labs Dr. Wattson Energy Monitoring Breakout
  --> https://www.tindie.com/products/UpbeatLabs/dr-wattson-energy-monitoring-board-2/

  This example demonstrates the event capabilities of the MCP39F521 used in Dr. Wattson.
  It can generate signals on the EVENT pin which can then be attached to an 
  externally interruptable pin on the Arduino to get notifications of events of 
  interest. Further details of which event occured, etc, can be obtained by querying
  the module's system Status and processing the result.

  In this example, we enable Voltage Sag, Voltage Surge, Over Current and Over Power
  events, and also set the appropriate limits when these events will get generated. 
  Voltage sag if voltage drops below 80v, Over current if current goes above 0.18 amps, 
  and Over Power if active power goes above 16 watts. When the event of interest happens
  you can see appropriate messages in the Serial output. The messages continue as long as 
  the event persists. 

  To trigger the Voltage Sag event, you can turn off power to your input. 
  To trigger Over Current and Over Power, you can turn on the load on your output. 
  The limits were set to be above the current and active power consumption of a
  CFL bulb - you can set appropriate limits for your load of choice. 

  To stop the Voltage Sag event, turn on the input power to restore voltage back. 
  To stop the Over Current and Over Power events, simply turn off your load (once
  input power has been restored). 

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
  interrupt pins 2 and 3. In this example, EVENT is connected to pin 3's
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
UpbeatLabs_MCP39F521_EventFlagLimits eventFlagLimits;

void setup() {                
  // initialize the digital pin as an output.
  pinMode(led, OUTPUT);     
  attachInterrupt(1, eventCB, CHANGE);
  Serial.begin(9600);  //turn on serial communication
  Serial.println("Upbeat Labs Dr. Wattson Event Example Sketch");
  Serial.println("********************************************");
  
  wattson.begin(); // Pass in the appropriate address. Defaults to 0x74

  uint32_t eventData = 0;
  int retVal = UpbeatLabs_MCP39F521::SUCCESS;
    
  retVal = wattson.setEventConfigurationRegister(eventData);

  retVal = wattson.readEventConfigRegister(&eventData);
  if (retVal != UpbeatLabs_MCP39F521::SUCCESS) {
    Serial.print("Error reading config register: "); Serial.println(retVal);
  }
  Serial.print("Event data: "); Serial.println(eventData);

  retVal = wattson.readEventFlagLimitRegisters(&eventFlagLimits);
  if (retVal != UpbeatLabs_MCP39F521::SUCCESS) {
    Serial.print("Error reading event flag limit registers: "); Serial.println(retVal);
  }
  Serial.print("Voltage Sag Limit: ");
  Serial.println(eventFlagLimits.voltageSagLimit/10.0f, 4);
  
  Serial.print("Voltage Surge Limit: ");
  Serial.println(eventFlagLimits.voltageSurgeLimit/10.f, 4);
  
  Serial.print("Over Current Limit: ");
  Serial.println(eventFlagLimits.overCurrentLimit/10000.0f, 4);
  
  Serial.print("Over Power Limit: ");
  Serial.println(eventFlagLimits.overPowerLimit/100.0f, 4);

  Serial.println("Set Event Flags...");
  eventFlagLimits.overCurrentLimit = 1800; // 0.18a
  eventFlagLimits.overPowerLimit = 1600; // 16w

  retVal = wattson.writeEventFlagLimitRegisters(&eventFlagLimits);

  UpbeatLabs_MCP39F521_DesignConfigData dData;
  retVal = wattson.readDesignConfigurationRegisters(&dData);

  // Map Voltage Sag Event to event pin
  bitSet(eventData, UpbeatLabs_MCP39F521::EVENT_VSAG_PIN);
  // Map Voltage Surge Event to event pin
  bitSet(eventData, UpbeatLabs_MCP39F521::EVENT_VSURGE_PIN);
  // Map Over Current Event to event pin
  bitSet(eventData, UpbeatLabs_MCP39F521::EVENT_OVERCUR_PIN);
  // Map Over Power Event to event pin
  bitSet(eventData, UpbeatLabs_MCP39F521::EVENT_OVERPOW_PIN);
  
  Serial.print("Event Config Register set to ");
  Serial.println(eventData);
    
  retVal = wattson.setEventConfigurationRegister(eventData);
}
 
void loop() {
  int retVal = UpbeatLabs_MCP39F521::SUCCESS;
  
  UpbeatLabs_MCP39F521_Data data;
  retVal = wattson.read(&data, NULL);
  if (retVal != UpbeatLabs_MCP39F521::SUCCESS) {
    Serial.print("Error reading energy data: "); Serial.println(retVal);
  }

  checkSystemStatus(data.systemStatus);
  
  delay(1000);


}

// Interrupt service routine for Events

void eventCB() {
  int state = digitalRead(3);
  digitalWrite(led, state);
} 


void checkSystemStatus(uint16_t systemStatus)
{
  if (bitRead(systemStatus, UpbeatLabs_MCP39F521::SYSTEM_EVENT) == 1) {
    Serial.println("event bit set"); 
  }

  if (bitRead(systemStatus, UpbeatLabs_MCP39F521::SYSTEM_VSAG) == 1) {
    Serial.println("VSAG bit set"); 
  }

  if (bitRead(systemStatus, UpbeatLabs_MCP39F521::SYSTEM_VSURGE) == 1) {
    Serial.println("VSURGE bit set"); 
  }

  if (bitRead(systemStatus, UpbeatLabs_MCP39F521::SYSTEM_OVERCUR) == 1) {
    Serial.println("OVERCUR bit set"); 
  }

  if (bitRead(systemStatus, UpbeatLabs_MCP39F521::SYSTEM_OVERPOW) == 1) {
    Serial.println("OVERPOW bit set"); 
  }
  
  if (bitRead(systemStatus, UpbeatLabs_MCP39F521::SYSTEM_SIGN_PA) == 1) {
    Serial.println("SIGN_PA bit set"); 
  }

  if (bitRead(systemStatus, UpbeatLabs_MCP39F521::SYSTEM_SIGN_PR) == 1) {
    Serial.println("SIGN_PR bit set"); 
  }
}
