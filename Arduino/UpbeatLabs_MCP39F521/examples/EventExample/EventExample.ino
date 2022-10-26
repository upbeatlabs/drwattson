/*************************************************** 
  This is a example sketch for Upbeat Labs Dr. Wattson Energy Monitoring Breakout
  --> https://www.protostax.com/products/dr-wattson-energy-monitoring-board-v2/

  This example demonstrates the event capabilities of the MCP39F521 used in Dr. Wattson.
  It can generate signals on the EVENT pin which can then be attached to an 
  externally interruptable pin on the Arduino to get notifications of events of 
  interest. Further details of which event occured, etc, can be obtained by querying
  the module's system Status and processing the result.

  In this example, we enable Voltage Sag, Voltage Surge, Over Current and Over Power
  events, and also set the appropriate limits when these events will get generated. 
  Voltage sag if voltage drops below 80v, Voltage Surge if the voltage goes above
  130v, Over current if current goes above 0.18 amps, 
  and Over Power if active power goes above 16 watts. When the event of interest happens
  you can see appropriate messages in the Serial output. The messages continue as long as 
  the event persists. The EVENT_LED will also stay lit when the triggering event condition
  persists and turns off when the event is cleared

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

// Use onboard LED 13 as the EVENT NOTIFICATION led
int EVENT_LED = 13;

#define OVER_CURRENT_LIMIT  1800  // 0.18a
#define OVER_POWER_LIMIT    1600    // 16w
#define VOLTAGE_SAG_LIMIT   800    // 80v
#define VOLTAGE_SURGE_LIMIT 1300 // 130v

UpbeatLabs_MCP39F521 wattson = UpbeatLabs_MCP39F521();
UpbeatLabs_MCP39F521_EventFlagLimits eventFlagLimits = {};

bool eventTriggered = false;

void setup() {                
  // initialize the digital pin as an output.
  pinMode(EVENT_LED, OUTPUT);     
  attachInterrupt(1, eventCB, CHANGE);
  Serial.begin(9600);  //turn on serial communication
  Serial.println("Upbeat Labs Dr. Wattson Event Example Sketch");
  Serial.println("********************************************");
  
  wattson.begin(); // Pass in the appropriate address. Defaults to 0x74

  uint32_t eventData = 0;
  int retVal = UpbeatLabs_MCP39F521::SUCCESS;
  
  Serial.println("Set Event Thresholds ...");
  eventFlagLimits.voltageSagLimit = VOLTAGE_SAG_LIMIT;
  eventFlagLimits.voltageSurgeLimit = VOLTAGE_SURGE_LIMIT;
  eventFlagLimits.overCurrentLimit = OVER_CURRENT_LIMIT; 
  eventFlagLimits.overPowerLimit = OVER_POWER_LIMIT; 

  retVal = wattson.writeEventFlagLimitRegisters(&eventFlagLimits);
  if (retVal != UpbeatLabs_MCP39F521::SUCCESS) {
    Serial.print("Error writing event thresholds!: "); Serial.println(retVal);
  }  
  
  // Print out the current thresholds
  printEventConfig(&eventFlagLimits);  

  // Turn on various event notifications
  // Map Voltage Sag Event to event pin
  bitSet(eventData, UpbeatLabs_MCP39F521::EVENT_VSAG_PIN);
  // Map Voltage Surge Event to event pin
  bitSet(eventData, UpbeatLabs_MCP39F521::EVENT_VSURGE_PIN);
  // Map Over Current Event to event pin
  bitSet(eventData, UpbeatLabs_MCP39F521::EVENT_OVERCUR_PIN);
  // Map Over Power Event to event pin
  bitSet(eventData, UpbeatLabs_MCP39F521::EVENT_OVERPOW_PIN);
    
  retVal = wattson.setEventConfigurationRegister(eventData);
  if (retVal != UpbeatLabs_MCP39F521::SUCCESS) {
    Serial.print("Error writing event configuration!: "); Serial.println(retVal);
  }    
  
  Serial.print("Event Config Register set to "); Serial.println(eventData);
  
}
 
void loop() {

  int retVal = UpbeatLabs_MCP39F521::SUCCESS;

  if (eventTriggered) {
    // If an event has been triggered, we can read the systemStatus
    // to see which conditions have been triggered
    UpbeatLabs_MCP39F521_Data data = {};
    retVal = wattson.read(&data, NULL);
    if (retVal != UpbeatLabs_MCP39F521::SUCCESS) {
      Serial.print("Error reading energy data: "); Serial.println(retVal);
    }
    checkSystemStatus(data.systemStatus);
    delay(1000); // So we are not bombarded with event messages when still triggered
  }
  delay(100);


}

// Interrupt service routine for Events

void eventCB() {
  int state = digitalRead(3);
  digitalWrite(EVENT_LED, state);
  eventTriggered = (state == HIGH);
} 


void checkSystemStatus(uint16_t systemStatus)
{
  if (bitRead(systemStatus, UpbeatLabs_MCP39F521::SYSTEM_EVENT) == 1) {
    Serial.println("EVENT has occurred!"); 
  }

  if (bitRead(systemStatus, UpbeatLabs_MCP39F521::SYSTEM_VSAG) == 1) {
    Serial.println("Voltage SAG condition"); 
  }

  if (bitRead(systemStatus, UpbeatLabs_MCP39F521::SYSTEM_VSURGE) == 1) {
    Serial.println("Voltage Surge condition"); 
  }

  if (bitRead(systemStatus, UpbeatLabs_MCP39F521::SYSTEM_OVERCUR) == 1) {
    Serial.println("Over Current condition"); 
  }

  if (bitRead(systemStatus, UpbeatLabs_MCP39F521::SYSTEM_OVERPOW) == 1) {
    Serial.println("Over Power condition"); 
  }

  // The sign of the active/reaction power is also indicated in the system
  // status register. This can tell us in which quadrant our power is.
  // We only want to do this when we have power - i.e when there is a
  // voltage sag, let's ignore this
  if (bitRead(systemStatus, UpbeatLabs_MCP39F521::SYSTEM_VSAG) == 0) {
    if (bitRead(systemStatus, UpbeatLabs_MCP39F521::SYSTEM_SIGN_PA) == 1) {
      Serial.println("Active Power is positive (import)"); 
    } else {
      Serial.println("Active Power is negative (export)"); 
    }

    if (bitRead(systemStatus, UpbeatLabs_MCP39F521::SYSTEM_SIGN_PR) == 1) {
      Serial.println("Reactive power is positive, inductive"); 
    } else {
      Serial.println("Reactive power is negative, capacitive"); 
    }
  }
}

void printEventConfig(UpbeatLabs_MCP39F521_EventFlagLimits *eventFlagLimits)
{
  Serial.print("Voltage Sag Limit: ");
  Serial.println(eventFlagLimits->voltageSagLimit/10.0f, 4);
  
  Serial.print("Voltage Surge Limit: ");
  Serial.println(eventFlagLimits->voltageSurgeLimit/10.f, 4);
  
  Serial.print("Over Current Limit: ");
  Serial.println(eventFlagLimits->overCurrentLimit/10000.0f, 4);
  
  Serial.print("Over Power Limit: ");
  Serial.println(eventFlagLimits->overPowerLimit/100.0f, 4);


}
