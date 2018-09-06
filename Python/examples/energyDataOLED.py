#!/usr/bin/python

#*****************************************************************************
# This is a example program for Upbeat Labs Dr. Wattson Energy Monitoring Breakout
# --> https://www.tindie.com/products/UpbeatLabs/dr-wattson-energy-monitoring-board-2/

# This example demonstrates getting Energy Data from Dr. Wattson.

# The program starts to poll the module for Energy data and prints it out in a loop.

# Turn on the input power to see the voltage RMS, line frequency values 
# change to the appropriate values. 

# Turn on the load attached to your output to see current RMS, power factor, 
# active, reactive and apparent power values change. 

# The communication happens over I2C. 2 pins are required to interface. 
# There are 4 selectable I2C address possibilities per board (selectable
# via two solder jumpers (that select each pin to be high or low). Based 
# on this, there are 4 possible addresses:

# I2C address  SJ1   SJ2
# 0x74         LOW   LOW
# 0x75         LOW   HIGH
# 0x76         HIGH  LOW
# 0x77         HIGH  HIGH

# Written by Sridhar Rajagopal for Upbeat Labs LLC.
# BSD license. All text above must be included in any redistribution

import UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521 as UpbeatLabs_MCP39F521
import subprocess as sp
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Raspberry Pi pin configuration:
RST = 17
# Note the following are only used with SPI:
DC = 27
SPI_PORT = 0
SPI_DEVICE = 0

disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

wattson = UpbeatLabs_MCP39F521.UpbeatLabs_MCP39F521()

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# First define some constants to allow easy resizing of shapes.
padding = 2
shape_width = 20
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = padding

# Load default font.
font = ImageFont.load_default()

while(1):
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    tmp = sp.call('clear',shell=True)
    (ret, result) = wattson.readEnergyData()
    print "VoltageRMS = " + str(result.voltageRMS)
    print "CurrentRMS = " + str(result.currentRMS)
    print "LineFrequency = " + str(result.lineFrequency)
    print "PowerFactor = " + str(result.powerFactor)
    print "ActivePower = " + str(result.activePower)
    print "ReactivePower = " + str(result.reactivePower)
    print "ApparentPower = " + str(result.apparentPower)
    # Write two lines of text.
    draw.text((x, top),    str("{:.2f}".format(result.voltageRMS)) + ' V @ ' + str("{:.2f}".format(result.lineFrequency)) + ' Hz',  font=font, fill=255)
    draw.text((x, top+10), 'Irms: ' + str("{:.4f}".format(result.currentRMS)) + ' A', font=font, fill=255)
    draw.text((x, top+20), 'PF: ' + str("{:.2f}".format(result.powerFactor)), font=font, fill=255)
    draw.text((x, top+30), 'ActiveP: ' + str("{:.2f}".format(result.activePower)) + 'W', font=font, fill=255)
    draw.text((x, top+40), 'ReactiveP: ' + str("{:.2f}".format(result.reactivePower)) + 'W', font=font, fill=255)
    draw.text((x, top+50), 'ApparentP: ' + str("{:.2f}".format(result.apparentPower)) + 'W', font=font, fill=255)


    # Display image.
    disp.image(image)
    disp.display()   
    time.sleep(1); 
