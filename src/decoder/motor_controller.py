class MotorControllerCANStatus():
    """CTRE TalonSRX/VictorSPX motor controller CAN bus status frame decoder

    The base arbitration ID for the TalonSRX is 0x02040000 and 0x01040000 for
    the VictorSPX.  The arbitration device ID is a 6-bit value between 0x00 and
    0x3F.  The arbtration status ID's are as follows:

        Status 1  = 0x041400 : Faults, Limit Switch State, Output Percent
        Status 2  = 0x041440 : Sticky Faults, Primary Sensor Position, Primary
                               Sensor Velocity, Output Current
        Status 3  = 0x041480
        Status 4  = 0x0414C0
        Status 5  = 0x041500
        Status 6  = 0x041540
        Status 7  = 0x041580
        Status 8  = 0x0415C0
        Status 9  = 0x041600
        Status 10 = 0x041640
        Status 11 = 0x041680
        Status 12 = 0x0416C0
        Status 13 = 0x041700
        Status 14 = 0x041740
        Status 15 = 0x041780

    The arbitraiton ID presented on the CAN bus is the logicl OR'ing of the base
    ID, device ID, and the status ID.  All of these arbitration ID's will
    include 8-bytes of data.  The specific decoding of the data is handled by
    the StatusXX() objects.  A bried description of the signals within the
    status frames are below:


    Attributes
    ----------
    status1 : dict
        The decoded status 1 signals
    status2 : dict
        The decoded status 2 signals


    Methods
    -------
    DecodeStatus1(data, timestamp)
        Decodes the data frame and updates the status1 dictionary
    DecodeStatus2(data, timestamp)
        Decodes the data frame and updates the status2 dictionary


    References
    ----------
    http://www.ni.com/white-paper/2732/en/
    https://github.com/CrossTheRoadElec/Phoenix-netmf/blob/master/CTRE/LowLevel/MotController_LowLevel.cs

    """

    def __init__(self):
        """
        Constructor creates the status attributes
        """

        self.status1 = {
            'timestamp' : 0.0,
            'hardware_failure' : 0,
            'reverse_limit_switch' : 0,
            'forward_limit_switch' : 0,
            'under_voltage' : 0,
            'reset_during_en' : 0,
            'sensor_out_of_phase' : 0,
            'sensor_overflow' : 0,
            'reverse_soft_limit' : 0,
            'forward_soft_limit' : 0,
            'hardware_esd_reset' : 0,
            'remote_loss_of_signal' : 0,
            'motor_output_percent' : 0.0,
            'fwd_limit_switch_closed' : 0,
            'rev_limit_switch_closed' : 0
        }
        self.status2 = {
            'timestamp' : 0.0,
            'output_current' : 0.0,
            'sensor_position' : 0.0,
            'sensor_velocity' : 0.0,
            'remote_loss_of_signal' : 0,
            'hardware_esd_reset' : 0,
            'reset_during_en' : 0,
            'sensor_out_of_phase' : 0,
            'sensor_overflow' : 0,
            'reverse_soft_limit' : 0,
            'forward_soft_limit' : 0,
            'reverse_limit_switch' : 0,
            'forward_limit_switch' : 0,
            'under_voltage' : 0
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
        self._GetFaults(data)
        self._GetMotorOutputPercent(data)
        self._GetFwdLimitSwitchClosed(data)
        self._GetRevLimitSwitchClosed(data)

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
        self._GetOutputCurrent(data)
        self._GetSensorPosition(data)
        self._GetSensorVelocity(data)
        self._GetStickyFaults(data)


    def _GetFaults(self, data):
        """
        Decodes and sets the motor controller motor faults.  See GetFaults for
        the CTRE implementation.

        Parameters
        ----------
        data : int
            An integer input of the 8-bytes of data

        """

        self.status1['hardware_failure']      = ((data >> 0) & 1)
        self.status1['reverse_limit_switch']  = ((data >> 1) & 1)
        self.status1['forward_limit_switch']  = ((data >> 2) & 1)
        self.status1['under_voltage']         = ((data >> 3) & 1)
        self.status1['reset_during_en']       = ((data >> 4) & 1)
        self.status1['sensor_out_of_phase']   = ((data >> 5) & 1)
        self.status1['sensor_overflow']       = ((data >> 6) & 1)
        self.status1['reverse_soft_limit']    = ((data >> (0x18 + 0)) & 1)
        self.status1['forward_soft_limit']    = ((data >> (0x18 + 1)) & 1)
        self.status1['hardware_esd_reset']    = ((data >> (0x18 + 2)) & 1)
        self.status1['remote_loss_of_signal'] = ((data >> (0x30 + 4)) & 1)


    def _GetMotorOutputPercent(self, data):
        """
        Decodes and sets the motor output percent.  See GetMotorOutputPercent
        for the CTRE implementation.

        Parameters
        ----------
        data : int
            An integer input of the 8-bytes of data

        """

        H = (data >> 24) & 0x07
        L = (data >> 32) & 0xFF
        raw = 0
        raw |= H
        raw <<= 8
        raw |= L
        raw <<= (32 - 11)
        raw >>= (32 - 11)
        self.status1['motor_output_percent'] = raw / 1023.0


    def _GetFwdLimitSwitchClosed(self, data):
        """
        Decodes and sets the forward limit switch.  See IsFwdLimitSwitchClosed
        for the CTRE implementation.

        Parameters
        ----------
        data : int
            An integer input of the 8-bytes of data

        """

        self.status1['fwd_limit_switch_closed'] = (data >> (0x18 + 7)) & 1


    def _GetRevLimitSwitchClosed(self, data):
        """
        Decodes and sets the reverse limit switch.  See IsRevLimitSwitchClosed
        for the CTRE implementation.

        Parameters
        ----------
        data : int
            An integer input of the 8-bytes of data

        """

        self.status1['rev_limit_switch_closed'] = (data >> (0x18 + 6)) & 1


    def _GetOutputCurrent(self, data):
        """
        Decodes and sets the motor output current.  See GetMotorOutputCurrent
        for the CTRE implementation.

        Parameters
        ----------
        data : int
            An integer input of the 8-bytes of data

        """

        H = (data >> 40) & 0xFF
        L = (data >> 48) & 0xC0
        raw = 0
        raw |= H
        raw <<= 8
        raw |= L
        raw >>= 6
        self.status2['output_current'] = raw * 0.125


    def _GetSensorPosition(self, data):
        """
        Decodes and sets the sensor position.  See GetSelectedSensorPosition
        for the CTRE implementation.

        Parameters
        ----------
        data : int
            An integer input of the 8-bytes of data

        """

        H = (data >> 0)
        M = (data >> 8)
        L = (data >> 16)
        PosDiv8 = (data >> (0x38 + 4)) & 1
        raw = 0
        raw |= H
        raw <<= 8
        raw |= M
        raw <<= 8
        raw |= L
        raw <<= (32 - 24)
        raw >>= (32 - 24)
        if PosDiv8 == 1:
            raw *= 8
        self.status2['sensor_position'] = raw


    def _GetSensorVelocity(self, data):
        """
        Decodes and sets the sensor velocity.  See GetSelectedSensorVelocity
        for the CTRE implementation.

        Parameters
        ----------
        data : int
            An integer input of the 8-bytes of data

        """

        H = (data >> 24)
        L = (data >> 32)
        VelDiv4 = (data >> (0x38 + 3)) & 1
        raw = 0
        raw |= H
        raw <<= 8
        raw |= L
        raw <<= (32 - 16)
        raw >>= (32 - 16)
        if VelDiv4 == 1:
            raw *= 4
        self.status2['sensor_velocity'] = raw


    def _GetStickyFaults(self, data):
        """
        Decodes and sets the sticky faults.  See GetStickyFaults
        for the CTRE implementation.

        Parameters
        ----------
        data : int
            An integer input of the 8-bytes of data

        """

        self.status2['remote_loss_of_signal'] = ((data >> (0x38 + 0)) & 1)
        self.status2['hardware_esd_reset'] =    ((data >> (0x38 + 1)) & 1)
        self.status2['reset_during_en'] =       ((data >> (0x38 + 2)) & 1)
        self.status2['sensor_out_of_phase'] =   ((data >> (0x38 + 5)) & 1)
        self.status2['sensor_overflow'] =       ((data >> (0x38 + 6)) & 1)
        self.status2['reverse_soft_limit'] =    ((data >> (0x30 + 0)) & 1)
        self.status2['forward_soft_limit'] =    ((data >> (0x30 + 1)) & 1)
        self.status2['reverse_limit_switch'] =  ((data >> (0x30 + 2)) & 1)
        self.status2['forward_limit_switch'] =  ((data >> (0x30 + 3)) & 1)
        self.status2['under_voltage'] =         ((data >> (0x30 + 4)) & 1)
