/*******************************************************************************
  This is a example sketch for Upbeat Labs Dr. Wattson Energy Monitoring Breakout
  --> https://www.tindie.com/products/UpbeatLabs/dr-wattson-energy-monitoring-board-2/

  This example demonstrates getting Energy Data from Dr. Wattson and writing
  it to an SD card in a comma separated (CSV) format. A button is used to
  toggle the data collection, so you can log the data when you are ready. 

  When the button toggles the measurement, the sketch starts to poll the 
  module for Energy data and prints it out. For ease of seeing the values, 
  use a program like screen to display the Serial output. The serial writes 
  the characters necessary to clear the screen on a regular terminal, which 
  means that the serial output will stay in place and just update over time. 

  Turn on the input power to see the voltage RMS, line frequency values 
  change to the appropriate values. 

  Turn on the load attached to your output to see current RMS, power factor, 
  active, reactive and apparent power values change.  

  All these values are written to the SD card in CSV format, which can then
  be used with a program like Excel to view/plot the data. The file name is
  of the form DATAnn.CSV. At the time of setup, a new file name is chosen that
  does not already exist, so the files will be DATA00.CSV, DATA01.CSV, DATA02.CSV
  and so on. The logging rotates to new files until DATA99.CSV. 

  The communication happens over I2C. 2 pins are required to interface. 
  There are 4 selectable I2C address possibilities per board (selectable
  via two solder jumpers (that select each pin to be high or low). Based 
  on this, there are 4 possible addresses:

  I2C address  SJ1   SJ2
  0x74         LOW   LOW
  0x75         LOW   HIGH
  0x76         HIGH  LOW
  0x77         HIGH  HIGH

  Dr. Wattson has two outputs, ZCD or Event, that are 
  used for notifications, and therefore will usually be 
  connected to an externally interruptable pin 
  (like pin2 or pin3 on Arduino Uno). In this example,
  ZCD and Event are not used.

  Button is connected to pin 4.
  
  * SD card attached to SPI bus as follows:
  ** MOSI - pin 11
  ** MISO - pin 12
  ** CLK - pin 13
  ** CS - pin 10
  
  LED is connected to pin 9
 
  Written by Sridhar Rajagopal for Upbeat Labs LLC.
  BSD license. All text above must be included in any redistribution
 */
 
#include <Wire.h>
#include "UpbeatLabs_MCP39F521.h"
#include <SD.h>
#include <Button.h>        //https://github.com/JChristensen/Button

#define BUTTON_PIN 4       //Connect a tactile button switch (or something similar)
                           //from Arduino pin 4 to ground.
                           
#define PULLUP true        //To keep things simple, we use the Arduino's internal pullup resistor.
#define INVERT true        //Since the pullup resistor will keep the pin high unless the
                           //switch is closed, this is negative logic, i.e. a high state
                           //means the button is NOT pressed. (Assuming a normally open switch.)
#define DEBOUNCE_MS 20     //A debounce time of 20 milliseconds usually works well for tactile button switches.

Button myBtn(BUTTON_PIN, PULLUP, INVERT, DEBOUNCE_MS);    //Declare the button

#define LED 9 // Connect an LED (via a 220ohm resistor) from pin 9 (anode) to GND (cathode). 

#define CHIP_SELECT 10

UpbeatLabs_MCP39F521 wattson = UpbeatLabs_MCP39F521();

bool readData = false;

char filename[] = "DATA00.CSV";

void setup() {       
  Serial.begin(9600);  //turn on serial communication
  Serial.println(F("**Upbeat Labs Dr. Wattson Example Sketch**"));
  Serial.println(F("Upbeat Labs Dr. Wattson Energy Data SD Card Logging Example Sketch"));
  Serial.println(F("******************************************************************"));
  
  // initialize the digital pin as an output.
  pinMode(LED, OUTPUT);     
  pinMode(CHIP_SELECT, OUTPUT);
    
  // see if the card is present and can be initialized:
  if (!SD.begin(CHIP_SELECT)) {
    Serial.println(F("*** SD Card failed, or not present ***"));
    // don't do anything more:
  }
    
  wattson.begin(); // Pass in the appropriate address. Defaults to 0x74

  // create a new file
  for (uint8_t i = 0; i < 100; i++) {
    filename[4] = i/10 + '0';
    filename[5] = i%10 + '0';
    if (! SD.exists(filename)) {
      Serial.print(F("Data file is ")); Serial.println(filename);
      // only open a new file if it doesn't exist
      break;  // leave the loop! filename will now be the one we desire
    }
  }
  
  Serial.println(F("**initialization complete.**"));
  
}
 
void loop() {
  myBtn.read();                    //Read the button
  if (myBtn.wasReleased()) {       //If the button was released, change the LED state
        readData = !readData;
        digitalWrite(LED, readData);
  }
  
  if (readData) {
    UpbeatLabs_MCP39F521_Data data;
    UpbeatLabs_MCP39F521_FormattedData fData;
    
    int readMCPretval = wattson.read(&data, NULL);
    unsigned long currentMillis = millis();
    
    if (readMCPretval == UpbeatLabs_MCP39F521::SUCCESS) {
      // Print stuff out
      Serial.write("\x1B" "c"); // Clear the screen on a regular terminal
      wattson.convertRawData(&data, &fData);
      printMCP39F521Data(&fData);
              
      // if the file is available, write to it:
      File dataFile = SD.open(filename, FILE_WRITE);

      if (dataFile) {
        dataFile.print(currentMillis);
        dataFile.print(",");
        dataFile.print(fData.currentRMS);
        dataFile.print(",");
        dataFile.print(fData.activePower);
        dataFile.print(",");
        dataFile.print(fData.reactivePower);
        dataFile.print(",");
        dataFile.println(fData.apparentPower);       
  
        // print to the serial port too:
        dataFile.close();
      }  
      // if the file isn't open, pop up an error:
      else {
        Serial.print(F("error opening ")); Serial.println(filename);
      } 
      
    } else {
      Serial.print(F("Error!")); Serial.println(readMCPretval);
    }
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
