# Upbeat Labs Dr. Wattson Energy Monitoring Board Library

Arduino Library for use with Dr. Wattson Energy Monitoring Board

![Dr. Wattson Energy Monitoring Board](https://cdn.tindiemedia.com/images/resize/kW19eEY1MdSF9HKyd494XWZnL00=/p/full-fit-in/2400x1600/i/89288/products/2017-12-27T05%3A09%3A50.171Z-DSC_9624%20%281%29.jpg)

[https://www.tindie.com/products/10722/](https://www.tindie.com/products/10722/)

## Contents

* **examples/** - Example sketches for the library (.ino). Run these from the Arduino IDE
* **UpbeatLabs_MCP39F521.h**  - header file for library
* **UpbeatLabs_MCP39F521.cpp** - implementation file for library
* **library.properties** - General library properties for Arduino package manager

## Installing

Copy the entire UpbeatLabs_MCP39F521 folder under drwattson/Arduino to your Arduino libraries location.

See [Installing Additional Arduino Libraries](https://www.arduino.cc/en/Guide/Libraries#toc5) for more information if needed (under **Manual installation**)

## Examples

Once the library is installed, you can navigate to the example sketches from your Arduino IDE and open them up to compile and run. 

* **GetEnergyData** - "Hello World" example to get metering data from your Dr. Wattson, including Voltage RMS, Current RMS, Power Factor, Active Power, Reactive Power with a simple call
* **EEPROMExample**	- 	Write to and read from 512 bytes of EEPROM memory available on MCP39F521  (organized as 32 pages of 16 bytes each)	
* **EventExample** - Get event callback interrupt notifications for different conditions like Voltage Sag (for example Power outage), Voltage Surge, Over Current  and Over Power over specified thresholds
* **EnergyAccumulationExample** - Turn on the energy accumulator to get cumulative energy consumption for Active and Reactive Energy

## License

A lot of time and effort has gone into providing this open source library. Please support Upbeat Labs by purchasing products from Upbeat Labs!

Written by Sridhar Rajagopal for Upbeat Labs. BSD license, all text above must be included in any redistribution
