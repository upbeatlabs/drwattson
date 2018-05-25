/*******************************************************************************
  This is a example sketch for Upbeat Labs Dr. Wattson Energy Monitoring Breakout
  --> https://www.tindie.com/products/UpbeatLabs/dr-wattson-energy-monitoring-board-2/

  This example was used to present at Maker Faire Bay Area 2018 at
  "Easy Energy Monitoring with Arduino* and Dr. Wattson"

  * and Raspberry Pi too! :-) 

  This example demonstrates getting Energy Data from Dr. Wattson and writing
  it to an SD card in a comma separated (CSV) format. A button is used to
  toggle the data collection, so you can log the data when you are ready. 
  The global variable readData is used to control whether data collection is 
  enabled on startup or not by setting its initial value to true or false.

  An RTC (DS1339 breakout) is used to note the actual time of observation.
  Please use the DS1339 example sketch to set the time on the breakout 
  (which is done one time) - the on-board battery will ensure that the 
  set time persists across resets and power-ups/downs. 

  When the button toggles the measurement, the sketch starts to poll the 
  module for Energy data and (optionally) prints it out (this is commented out). 
  For ease of seeing the values, use a program like screen to display the 
  Serial output. The serial writes the characters necessary to clear the 
  screen on a regular terminal, which means that the serial output will 
  stay in place and just update over time. 

  Turn on the input power to see the voltage RMS, line frequency values 
  change to the appropriate values. 

  Turn on the load attached to your output to see current RMS, power factor, 
  active, reactive and apparent power values change.  

  All these values are written to the SD card in CSV format, which can then
  be used with a program like Excel to view/plot the data.  The file name is
  of the form DATAnn.CSV. At the time of setup, a new file name is chosen that
  does not already exist, so the files will be DATA00.CSV, DATA01.CSV, DATA02.CSV
  and so on. The logging rotates to new files until DATA99.CSV. 

  The CSV file also includes a header which is written to initially, so the 
  columns are named when used with a program like Excel. This can also be 
  imported into a database like MySQL. 

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
  STATUS_LED is connected to pin 8

  The DS1339 Breakout Board uses I2C for communication, and 
  is therefore also hooked up to SDA and SCL on the Arduino
  (pins A4 and A5). The SQW/INT pin can be connected to an
  externally interruptable pin like pin 2 and be used to 
  wake up the Arduino on an alarm set on the DS1339. 
 
  Written by Sridhar Rajagopal for Upbeat Labs LLC.
  BSD license. All text above must be included in any redistribution
 */

#include <avr/wdt.h>
#define Reset_AVR() wdt_enable(WDTO_1S); while(1) {}
 
#include <Wire.h>
#include <EEPROM.h>
#include "UpbeatLabs_MCP39F521.h"
#include <DS1339.h>
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
#define STATUS_LED 8 // Connect an LED (via a 220ohm resistor) from pin 8 (anode) to GND (cathode). 

#define CHIP_SELECT 10

int INT_PIN = 2; // INTerrupt pin from the RTC. On Arduino Uno, this should be mapped to digital pin 2 or pin 3, which support external interrupts
int int_number = 0; // On Arduino Uno, INT0 corresponds to pin 2, and INT1 to pin 3

DS1339 RTC = DS1339(INT_PIN, int_number);

UpbeatLabs_MCP39F521 wattson = UpbeatLabs_MCP39F521();

bool readData = true; // start with reading data
bool statusFlip = false;
bool errorStat = false;
bool sdPresent = false;

char filename[] = "DATA00.CSV";

int eepromErrRecLocation = 0;

#define EEPROM_DEBUG

#ifdef EEPROM_DEBUG
  #define EEPROM_WRITE(x, y) EEPROM.write(x, y)
#else
  #define EEPROM_WRITE(x, y)
#endif

#ifdef DEBUG
 #define DEBUG_PRINT(x)  Serial.print (x)
 #define DEBUG_PRINTLN(x) Serial.println (x)
#else
 #define DEBUG_PRINT(x)
 #define DEBUG_PRINTLN(x)
#endif

void blink() {
  for(int i=0; i<5; i++) {
    digitalWrite(LED, HIGH);
    digitalWrite(STATUS_LED, HIGH);
    delay(100);
    digitalWrite(LED, LOW);
    digitalWrite(STATUS_LED, LOW);
    delay(100);
  }
}

void setup() {       
  Serial.begin(9600);  //turn on serial communication
  Serial.println(F("**Upbeat Labs Dr. Wattson Example Sketch**"));
  Serial.println(F("Upbeat Labs Dr. Wattson Energy Data SD Card Logging Example Sketch"));
  Serial.println(F("******************************************************************"));
  
  // initialize the digital pin as an output.
  pinMode(LED, OUTPUT);     
  pinMode(STATUS_LED, OUTPUT);
  pinMode(CHIP_SELECT, OUTPUT);

  // To show visual bootup
  blink();

  // initialize DS1339
  pinMode(INT_PIN, INPUT);
  digitalWrite(INT_PIN, HIGH);
  RTC.start(); // ensure RTC oscillator is running, if not already
  
  if(!RTC.time_is_set()) // set a time, if none set already...
  {
    Serial.print("Clock not set. ");
    set_time();
  }
  
  // If the oscillator is borked (or not really talking to the RTC), try to warn about it
  if(!RTC.time_is_set())
  {
    Serial.println("Clock did not set! Check that its oscillator is working.");
    errorStat = true;
  }
    
  // see if the card is present and can be initialized:
  if (!SD.begin(CHIP_SELECT)) {
    Serial.println(F("*** SD Card failed, or not present ***"));
    digitalWrite(LED, HIGH);
    digitalWrite(STATUS_LED, HIGH);
    errorStat = true;
    sdPresent = false;
  } else {
    sdPresent = true;
  }
    
  wattson.begin(); // Pass in the appropriate address. Defaults to 0x74

  // create a new file
  for (uint8_t i = 0; i < 100; i++) {
    filename[4] = i/10 + '0';
    filename[5] = i%10 + '0';
    if (! SD.exists(filename)) {
      Serial.print(F("Data file is ")); Serial.println(filename);
      // only open a new file if it doesn't exist
      eepromErrRecLocation = i;
      break;  // leave the loop! filename will now be the one we desire
    }
  }
  
  // Clear any previous energy accumulation
  wattson.enableEnergyAccumulation(false);   

  // Set read LED's status
  digitalWrite(LED, readData);
  if (readData) {
    // Wait for sometime for registers to reset before re-enabling them
    delay(1000);
    Serial.println(F("readData is TRUE - Turn on Energy Accumulation"));
    wattson.enableEnergyAccumulation(true);       
  } 
  Serial.println(F("**initialization complete.**"));
  
}

void nap()
{
  // Dummy function. We don't actually want to do anything here, just use an interrupt to wake up.
  //RTC.clear_interrupt();
  // For some reason, sending commands to clear the interrupt on the RTC here does not work. Maybe Wire uses interrupts itself?
  Serial.print(".");

}
 
void loop() {
  // Flip STATUS_LED every loop. Gives visual indication of "heartbeat"
  if (!errorStat) {
    statusFlip = !statusFlip;
    digitalWrite(STATUS_LED, statusFlip);
  }
   
  myBtn.read();                    //Read the button
  if (myBtn.wasReleased()) {       //If the button was released, change the LED state
        readData = !readData;
        digitalWrite(LED, readData);
        if (readData) {
          wattson.enableEnergyAccumulation(true);       
        } else {   
          wattson.enableEnergyAccumulation(false);   
        }
  }
  
  if (readData) {
    UpbeatLabs_MCP39F521_Data data;
    UpbeatLabs_MCP39F521_FormattedData fData;

    UpbeatLabs_MCP39F521_AccumData aData;
    UpbeatLabs_MCP39F521_FormattedAccumData afData;

    
    int readMCPretval = wattson.read(&data, &aData);
    unsigned long currentMillis = millis();
    RTC.readTime();
    
    if (readMCPretval == UpbeatLabs_MCP39F521::SUCCESS) {
      // Print stuff out
      //Serial.write("\x1B" "c"); // Clear the screen on a regular terminal
      wattson.convertRawData(&data, &fData);
      wattson.convertRawAccumData(&aData, &afData);

      //printMCP39F521Data(&fData);
      //printMCP39F521AccumData(&afData);

      if (sdPresent) {
        static bool doOnce = true;

        // if the file is available, write to it:
        File dataFile = SD.open(filename, FILE_WRITE);

        if (dataFile) {
          if (doOnce) {
            Serial.print(F("Writing header to ")); Serial.println(filename);
          
            dataFile.print(F("observation_time,"));
            dataFile.print(F("Vrms,"));
            dataFile.print(F("Crms,"));
            dataFile.print(F("powerFactor,"));
            dataFile.print(F("activePower,"));
            dataFile.print(F("reactivePower,"));
            dataFile.print(F("apparentPower,"));
            dataFile.print(F("activeEnergyImport,"));
            dataFile.print(F("activeEnergyExport,"));
            dataFile.print(F("reactiveEnergyImport,"));
            dataFile.println(F("reactiveEnergyExport"));
            
            doOnce = false;
          }

          
          char curTime[256];
          sprintf(curTime, "%d/%d/%d %d:%d:%d", RTC.getMonths(), RTC.getDays(), 
                  RTC.getYears(), RTC.getHours(), RTC.getMinutes(), RTC.getSeconds());
          dataFile.print(curTime);
          dataFile.print(F(","));
          dataFile.print(fData.voltageRMS);
          dataFile.print(F(","));
          dataFile.print(fData.currentRMS);
          dataFile.print(F(","));
          dataFile.print(fData.powerFactor);
          dataFile.print(F(","));
          dataFile.print(fData.activePower);
          dataFile.print(F(","));
          dataFile.print(fData.reactivePower);
          dataFile.print(F(","));
          dataFile.print(fData.apparentPower);
          dataFile.print(F(","));
          dataFile.print(afData.activeEnergyImport);
          dataFile.print(F(","));
          dataFile.print(afData.activeEnergyExport);
          dataFile.print(F(","));
          dataFile.print(afData.reactiveEnergyImport);
          dataFile.print(F(","));
          dataFile.println(afData.reactiveEnergyExport);
               
  
          // print to the serial port too:
          dataFile.close();
        }  
        // if the file isn't open, pop up an error:
        else {
          Serial.print(F("error opening ")); Serial.println(filename);
          errorStat = true;
          EEPROM_WRITE(eepromErrRecLocation, 1);
          delay(100);
          Reset_AVR();
        } 
      } else { // (if sdPresent)
        Serial.println(F("SD card NOT present! "));
      }
      
    } else {
      Serial.print(F("Error!")); Serial.println(readMCPretval);
      errorStat = true;
      EEPROM_WRITE(eepromErrRecLocation, 2);
      delay(100);
      Reset_AVR();
    }
  }
  delay(500);
}


void printMCP39F521Data(UpbeatLabs_MCP39F521_FormattedData *data)
{
  Serial.print(F("Voltage = ")); Serial.println(data->voltageRMS, 4);
  Serial.print(F("Current = ")); Serial.println(data->currentRMS, 4);
  Serial.print(F("Line Frequency = ")); Serial.println(data->lineFrequency, 4);
  Serial.print(F("Analog Input Voltage = ")); Serial.println(data->analogInputVoltage, 4);
  Serial.print(F("Power Factor = ")); Serial.println(data->powerFactor, 4);
  Serial.print(F("Active Power = ")); Serial.println(data->activePower, 4);
  Serial.print(F("Reactive Power = ")); Serial.println(data->reactivePower, 4);
  Serial.print(F("Apparent Power = ")); Serial.println(data->apparentPower, 4);
}


void printMCP39F521AccumData(UpbeatLabs_MCP39F521_FormattedAccumData *data)
{
  Serial.print(F("Active Energy Import = ")); Serial.println(data->activeEnergyImport, 4);
  Serial.print(F("Active Energy Export = ")); Serial.println(data->activeEnergyExport, 4);
  Serial.print(F("Reactive Energy Import = ")); Serial.println(data->reactiveEnergyImport, 4);
  Serial.print(F("Reactive Energy Export = ")); Serial.println(data->reactiveEnergyExport, 4);
}


int read_int(char sep)
{
  static byte c;
  static int i;

  i = 0;
  while (1)
  {
    while (!Serial.available())
    {;}
 
    c = Serial.read();
    // Serial.write(c);
  
    if (c == sep)
    {
      // Serial.print("Return value is");
      // Serial.println(i);
      return i;
    }
    if (isdigit(c))
    {
      i = i * 10 + c - '0';
    }
    else
    {
      Serial.print(F("\r\nERROR: \""));
      Serial.write(c);
      Serial.print(F("\" is not a digit\r\n"));
      return -1;
    }
  }
}

int read_int(int numbytes)
{
  static byte c;
  static int i;
  int num = 0;

  i = 0;
  while (1)
  {
    while (!Serial.available())
    {;}
 
    c = Serial.read();
    num++;
    // Serial.write(c);
  
    if (isdigit(c))
    {
      i = i * 10 + c - '0';
    }
    else
    {
      Serial.print(F("\r\nERROR: \""));
      Serial.write(c);
      Serial.print(F("\" is not a digit\r\n"));
      return -1;
    }
    if (num == numbytes)
    {
      // Serial.print("Return value is");
      // Serial.println(i);
      return i;
    }
  }
}

int read_date(int *year, int *month, int *day, int *hour, int* minute, int* second)
{

  *year = read_int(4);
  *month = read_int(2);
  *day = read_int(' ');
  *hour = read_int(':');
  *minute = read_int(':');
  *second = read_int(2);

  return 0;
}

void set_time()
{
    Serial.println("Enter date and time (YYYYMMDD HH:MM:SS)");
    int year, month, day, hour, minute, second;
    int result = read_date(&year, &month, &day, &hour, &minute, &second);
    if (result != 0) {
      Serial.println(F("Date not in correct format!"));
      return;
    } 
    
    // set initially to epoch
    RTC.setSeconds(second);
    RTC.setMinutes(minute);
    RTC.setHours(hour);
    RTC.setDays(day);
    RTC.setMonths(month);
    RTC.setYears(year);
    RTC.writeTime();
    read_time();
}

void read_time() 
{
  Serial.print ("The current time is ");
  RTC.readTime(); // update RTC library's buffers from chip
  printTime(0);
  Serial.println();

}

void printTime(byte type)
{
  // Print a formatted string of the current date and time.
  // If 'type' is non-zero, print as an alarm value (seconds thru DOW/month only)
  // This function assumes the desired time values are already present in the RTC library buffer (e.g. readTime() has been called recently)

  if(!type)
  {
    Serial.print(int(RTC.getMonths()));
    Serial.print(F("/"));  
    Serial.print(int(RTC.getDays()));
    Serial.print(F("/"));  
    Serial.print(RTC.getYears());
  }
  else
  {
    //if(RTC.getDays() == 0) // Day-Of-Week repeating alarm will have DayOfWeek *instead* of date, so print that.
    {
      Serial.print(int(RTC.getDayOfWeek()));
      Serial.print(F("th day of week, "));
    }
    //else
    {
      Serial.print(int(RTC.getDays()));
      Serial.print(F("th day of month, "));      
    }
  }
  
  Serial.print("  ");
  Serial.print(int(RTC.getHours()));
  Serial.print(":");
  Serial.print(int(RTC.getMinutes()));
  Serial.print(":");
  Serial.print(int(RTC.getSeconds()));  
}


