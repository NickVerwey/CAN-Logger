import os

def Read_CAN_Message(f):
    """Read_CAN_Message will read one CAN frame's worth of data based upon the
    CAN_message_t type found in the FlexCAN library.  The data will be changed
    from little-endian to big-endian.

    Input(s)
    ----------
    f : file object
        This is the file object of the binary file captured by the CAN-logger

    Return(s)
    ----------
    arbID : string
        This is the 4-byte CAN arbitration ID
    timeStamp : string
        This is the hardware timestamp of the incomming frame.  For the Teensy
        3.6, this time stamp is 1-byte unsigned integer in units of
        microseconds.
    flags : string
        This is the 1-byte CAN flags
    length : string
        This is the 1-byte length describing the length of valid data in the
        data frame
    data : string
        This is the 8-byte data

    """
    
    arbID = f.read(4).hex()
    arbID = arbID[6:8] + arbID[4:6] + arbID[2:4] + arbID[0:2]
    timeStamp = f.read(2).hex()
    timeStamp = timeStamp[2:4] + timeStamp[0:2]
    flags = f.read(1).hex()
    length = f.read(1).hex()
    data = f.read(8).hex()
    data = data[14:16] + data[12:14] + data[10:12] + data[8:10] + data[6:8] + data[4:6] + data[2:4] + data[0:2]
    return [arbID, timeStamp, flags, length, data]


def Decode_Arb_ID(arbID):
    """ The Decode_Arb_ID will decode the arbitraion ID based upon the CTRE/FRC
    CANbus implementation.

    Input(s)
    ----------
    arbID : bytes
        This is the 4-byte CAN arbitration ID

    Return(s)
    ----------
    deviceType : string
        This is the 16-bit value representing the device
    frameType : string
        This is the 10-bit value representing the frame type
    deviceID : string
        This is a unique 6-bit value of the specific device

    """

    deviceType = '0x'+arbID[0:4]
    frameType = '0x'+hex(int(arbID[4:8], 16) & 0xFFC0)[2:].zfill(4)
    deviceID = int(arbID[6:8], 16) & 0x003F
    return [deviceType, frameType, deviceID]
    

def Decode_And_Save_As_CSV():
    """ Decode_And_Save_As_CSV will read up the binary file and decode each CAN
    message and save it to a comma delimited file.

    Input(s)
    ----------


    Output(s)
    ----------


    """

    rolloverTimestamp = 0
    with open(os.path.join(os.path.dirname(__file__), 'log_file.bin'), 'rb') as inFile:
        arbID, timeStamp, flags, length, data = Read_CAN_Message(inFile)
        lastTimestamp = int(timeStamp, 16)
        with open(os.path.join(os.path.dirname(__file__), 'log_file.csv'), 'w') as outFile:
            outFile.write('Device_Type,Frame_Type,Device_ID,Timestamp(ms),Flags,Length,Data\n')
            while arbID:
                deviceType, frameType, deviceID = Decode_Arb_ID(arbID)
                timeStamp = int(timeStamp,  16)
                if timeStamp - lastTimestamp < -1000:
                    rolloverTimestamp += 1<<16
                lastTimestamp = timeStamp
                timeStamp+=rolloverTimestamp
                outFile.write('%s,%s,%i,%.6f,%s,%s,%s\n' % (deviceType, frameType, deviceID, timeStamp/1e3, flags, length, data))
                arbID, timeStamp, flags, length, data = Read_CAN_Message(inFile)


Decode_And_Save_As_CSV()