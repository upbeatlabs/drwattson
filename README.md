# Upbeat Labs Dr. Wattson Energy Monitoring Board Library

** Please note! The repository has been updated to split out the libraries into their own github repositories. If you have been using this before for all the source code, please move over to cloning/forking the new repositories instead! This repository will be used to store the details pertaining to Dr. Wattson, such as the User Manual, the README, and other pertinent information**

Dr. Wattson is an Energy Monitoring Board for Arduino, Raspberry Pi and other Maker-Friendly Microcontrollers. Easily integrate quality AC energy measurements into your next project!

Based on the **MCP39F521**, a single-phase power monitoring chip from **Microchip**, the board is designed to be tolerant of a wide range of voltages, which means that it can also be used with the Raspberry Pi or any other 3.3v MCUs just as easily.

The unit comes pre-calibrated, enabling you to start taking quality measurements from 90-240v, at either 50 or 60 Hz, and for currents up to 15A. You don't need any additional CT/VT or other components.  With the libraries here, you can start taking measurements on the get-go with just a couple of simple commands.

If you are a more advanced user, you have a wide range of functionality available from the rich library, as well as the ability to tweak the hardware to suit your needs and recalibrate using the library.

![Dr. Wattson Energy Monitoring Board](https://cdn.shopify.com/s/files/1/0082/6248/4004/products/DrWattsonV2_title.jpg?v=1661905914)


[Learn more and get it here!](https://www.protostax.com/products/dr-wattson-energy-monitoring-board-v2/)

## Contents

* **LICENSE** - the license file (BSD 3-clause license)
* **README.md** - this file!
* **DrWattsonUserManual.pdf** - the User Manual for Dr. Wattson. It has all the information you need to get started with Dr. Wattson!

## Libraries

The following libraries are currently available:

* Arduino - [UpbeatLabs_MCP39F521](https://github.com/upbeatlabs/UpbeatLabs_MCP39F521)
* Python - [UpbeatLabs_Python_MCP39F521](https://github.com/upbeatlabs/UpbeatLabs_Python_MCP39F521) (using smbus2). Use with Raspberry Pi and other single-board computers (like BeagleBone Black)

The libraries come with lots of examples:
* Getting energy data - "Hello World" example to get metering data from your Dr. Wattson, including Voltage RMS, Current RMS, Power Factor, Active Power, Reactive Power with a simple call
* Events - Get event callback interrupt notifications for different conditions like Voltage Sag (for example Power outage), Voltage Surge, Over Current and Over Power over specified thresholds and figure out which conditions were triggered
* Energy Accumulation - Turn on the energy accumulator to get cumulative energy consumption for Active and Reactive Energy
* EEPROM - Write to and read from 512 bytes of EEPROM memory available on MCP39F521 (organized as 32 pages of 16 bytes each). The library abstracts out the details and makes the usage very simple
* Data logger - Get energy data and log it in CSV format to an SD card, using an RTC to note the time of observation. Turn on/off data recording with a button, and the example includes log rotation.
* AWS IoT - Send energy data to AWS IoT over MQTT (on Raspberry Pi using the Python version)

## License

A lot of time and effort has gone into providing this open source library. Please support Upbeat Labs by purchasing products from Upbeat Labs!

Written by Sridhar Rajagopal for Upbeat Labs. BSD license, all text above must be included in any redistribution
