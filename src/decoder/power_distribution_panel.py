class PDPCANStatus():
    """CTRE PDP CAN bus status frame decoder

    The base arbitration ID for the Power Distribution Panel is 0x08040000.  
    The arbitration device ID is a 6-bit value between 0x00 and 0x3F.  The 
    arbitration status ID's are as follows:

        Status 1  = 0x1400 : Current of Channels 0-5
        Status 2  = 0x1440 : Current of Channels 6-11
        Status 3  = 0x1480 : Current of Channels 12-15, Voltage

    The arbitration ID presented on the CAN bus is the logical OR'ing of the base
    ID, device ID, and the status ID.  All of these arbitration ID's will
    include 8-bytes of data.  The specific decoding of the data is handled by
    the StatusXX() objects.  A brief description of the signals within the
    status frames are below:


    Attributes
    ----------
    status1 : dict
        The decoded status 1 signals
    status2 : dict
        The decoded status 2 signals
    status3 : dict
        The decoded status 3 signals


    Methods
    -------
    DecodeStatus1(data, timestamp)
        Runs GetCurrent() for the relevent data and updates the status1 
        dictionary
    DecodeStatus2(data, timestamp)
        Runs GetCurrent() for the relevent data and updates the status2
        dictionary
    DecodeStatus3(data, timestamp)
        Runs GetCurrent() as well as GetVoltage() for the relevent data and
        updates the status3 dictionary 
    GetCurrent(data, arbid)
        Decodes the data provided by DecodeStatusX methods to determine the
        current in amperes
    GetVoltage(data)
        Decodes the data provided by DecodeStatus3 method to determine the
        voltage

    References
    ----------
    http://www.ni.com/white-paper/2732/en/
    https://github.com/CrossTheRoadElec/Phoenix-netmf/blob/master/CTRE/Power/PowerDistributionPanel.cs

    """

    def __init__(self):
        """
        Constructor creates the status attributes
        """
        
        self.status1 = {
            'timestamp' : 0.0,
            'chan_0' : 0.0,
            'chan_1' : 0.0,
            'chan_2' : 0.0,
            'chan_3' : 0.0,
            'chan_4' : 0.0,
            'chan_5' : 0.0

        }
        self.status2 = {
            'timestamp'  : 0.0,
            'chan_6' : 0.0,
            'chan_7' : 0.0,
            'chan_8' : 0.0,
            'chan_9' : 0.0,
            'chan_10' : 0.0,
            'chan_11' : 0.0
        }
        self.status3 = {
            'timestamp'  : 0.0,
            'chan_12' : 0.0,
            'chan_13' : 0.0,
            'chan_14' : 0.0,
            'chan_15' : 0.0,
            'voltage'    : 0.0
        }


    def DecodeStatus1(self, data, timestamp):
        """
        Decodes the 8-byte CAN data frame and sets the local attributes with the
        new values.
        
        Parameters
        ----------
        data : int
            An integer input of the 8-bytes of data
        timestamp : float
            The time the CAN controller received the data frame
        """
        self.status1['timestamp'] = timestamp
        CurrentList = self.GetCurrent(data)
        keys = ['chan_0', 'chan_1','chan_2','chan_3','chan_4','chan_5']
        self.status1.update(dict(zip(keys, CurrentList)))
        
    def DecodeStatus2(self, data, timestamp):
        """
        Decodes the 8-byte CAN data frame and sets the local attributes with the
        new values.
        
        Parameters
        ----------
        data : int
            An integer input of the 8-bytes of data
        timestamp : float
            The time the CAN controller received the data frame
        """        
        self.status2['timestamp'] = timestamp
        CurrentList = self.GetCurrent(data)
        keys = ['chan_6','chan_7','chan_8','chan_9','chan_10','chan_111']
        self.status2.update(dict(zip(keys, CurrrentList)))
        
    def DecodeStatus3(self, data, timestamp):
        """
        Decodes the 8-byte CAN data frame and sets the local attributes with the
        new values.
        
        Parameters
        ----------
        data : int
            An integer input of the 8-bytes of data
        timestamp : float
            The time the CAN controller received the data frame
        """        
        self.status3['timestamp'] = timestamp
        CurrentList = self.GetCurrent(data)
        keys = ['chan_12','chan_13','chan_14', 'chan_15']
        self.status3.update(dict(zip(keys, CurrentList)))
        
    def GetCurrent(self, data):
        """
        Decodes the 8-byte CAN data frame to find the current for each channel
        and returns a list of results to the DecodeStatusX that called the method
        
        Parameters
        ----------
        arbid : int
            The base arbitration ID for each Status frame
        data : int
            An integer input of the 8-bytes of data
        """        
        CurrentScalar = 0.125
        CurrentList = [0.0,0.0,0.0,0.0,0.0,0.0]
        
        hexdata = hex(data)
        
        CurrentList[0] = int(str(hexdata)[0:2] + str(hexdata)[-2:],16)
        CurrentList[0] <<= 2
        CurrentList[0] |= ((data >> 14) & 0x03)
        
        CurrentList[1] = ((data >> 8) & 0x3F)
        CurrentList[1] <<= 4
        CurrentList[1] |= ((data >> 20) & 0x0F)
        
        CurrentList[2] = ((data >> 16) & 0x0F)
        CurrentList[2] <<= 6
        CurrentList[2] |= ((data >> 26) & 0x3F)
        
        CurrentList[3] = ((data >> 24) & 0x03)
        CurrentList[3] <<= 8
        CurrentList[3] |= (int(str(hexdata)[0:2] + str(hexdata)[-2:],16) >> 32)
        
        CurrentList[4] = (int(str(hexdata)[0:2] + str(hexdata)[-2:],16) >> 40)
        CurrentList[4] <<= 2
        CurrentList[4] |= ((data >> 54) & 0x03)
        
        CurrentList[5] = ((data >> 48) & 0x3F)
        CurrentList[5] <<= 4
        CurrentList[5] |= ((data >> 60) & 0x0F)  
        
        CurrentList = [i * CurrentScalar for i in CurrentList]
        
        return CurrentList
    
    def GetVoltage(self, data):
        """
        Decodes the 8-byte CAN data frame to determine the voltage and returns
        the result to the DecodeStatus3 method
        
        Parameters
        ----------
        data : int
            An integer input of the 8-bytes of data
        """          
        VoltNum = hex(data >> 48)
        VoltNum = int(str(VoltNum)[0:2] + str(VoltNum)[-2:],16)
        
        retval = (.05 * VoltNum) + 4
        return retval
    
    
"""
For the purpose of testing. Allows for arbitrary data to be input.
"""
#py = PDPCANStatus()
#data = 0x56adff0000000000
#timestamp = 2
#py.DecodeStatus1(data,timestamp)