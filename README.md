# CAN-Logger

This project is all about logging/parsing/plotting FRC robot CAN traffic.
[![Build Status](https://travis-ci.org/FRC4607/CAN-Logger.png?branch=master)](https://travis-ci.org/FRC4607/CAN-Logger)
[![Coverage Status](https://coveralls.io/repos/github/FRC4607/CAN-Logger/badge.svg?branch=master)](https://coveralls.io/github/FRC4607/CAN-Logger?branch=master)

## Project Goals and Purpse

The primary goals of this project are to make CAN-bus logging simple, robust,
and Robo-RIO CPU-free.  The logger should be as simple as loading firmware on
the device and connecting it to the CAN-bus.  The logger needs to work
throughout the year with minimal effort.  Ideally, the only interaction with the
logger will be to remove the log files for data processing.  Finally, being a
Python team and GIL-limited, moving all CAN-bus logging "off board" will save
CPU cycles.

## Hardware

The $30 [Teensy 3.6](https://www.pjrc.com/teensy/) was choosen (thanks to Chris
Roadfeldt for the suggestion) along with a $16 [Dual CAN-bus Adapter](https://www.tindie.com/products/Fusion/dual-can-bus-adapter-for-teensy-35-36/).
Only a single CAN-bus is needed for this project, but the second bus could be
used for future expansion.  There are versions of both pieces of hardware which
supprt a single CAN-bus and are a bit cheaper.  The Dual Can-bus Adapter will
need to be soldered to the Teensy using
[header pins](https://www.pjrc.com/store/header_20x1.html).  Also, a micro-SD
will be needed for log file storage and a
[USB cable](https://www.pjrc.com/store/cable_usb_micro_b.html) is needed to load
sketches (programs) onto the Teensy.  This completes the hardware needed for the
Embedded CAN-bus Logger.

*Need to add a section about assembly.  Include CAD files for printed case.
Describe the power options.  Could be powered off of USB or could be powered off
of the robots VRM.

## Firmware

The firmware that gets loaded onto the Teensy is stored in the src/logger/
directory.  The purpose of the firmware is to grab CAN frames off of the bus and
store them onto the SD card.  To do this, the
[FlexCAN library](https://github.com/collin80/FlexCAN_Library) will be used to
capture frames from the CAN-bus and the
[SDFat Library](https://github.com/greiman/SdFat) will be used to write the
captured data to the SD card.

*Need to add a section about loading the firmware onto the Teensy.*

## Software

The software for log file decoding is stored in the src/decoder/ directory.
There are three classes which can be used by an application to decode the log
file.  The `MotorControllerCANStatus` class is used to decode status frames for
the CTRE Talon SRX / Victor SPX.  The `PneumaticsControllerCANStatus` class is
used to decode status frames from the CTRE Pneumatics Conrol Module.  Finally,
the `PowerDistributionCANStatus` class is used to decode the status frames from
the CTRE Power Distribution Panel.

*Need to add examples in the src/examples/ folder.*

## CAD

The CAD for the Teensy case is stored in the cad directory.
