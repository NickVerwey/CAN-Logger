class MotorControllerCANStatus:
    """CTRE TalonSRX/VictorSPX motor controller CAN bus status frame decoder

    The base arbitration ID for the TalonSRX is 0x02040000 and 0x01040000 for
    the VictorSPX.  The arbitration device ID is a 6-bit value between 0x00 and
    0x3F.  The arbtration status ID's are as follows:

        STATUS_01 = 0x041400
        STATUS_02 = 0x041440
        STATUS_03 = 0x041480
        STATUS_04 = 0x0414C0
        STATUS_05 = 0x041500
        STATUS_06 = 0x041540
        STATUS_07 = 0x041580
        STATUS_08 = 0x0415C0
        STATUS_09 = 0x041600
        STATUS_10 = 0x041640
        STATUS_11 = 0x041680
        STATUS_12 = 0x0416C0
        STATUS_13 = 0x041700
        STATUS_14 = 0x041740
        STATUS_15 = 0x041780

    The arbitraiton ID presented on the CAN bus is the logicl OR'ing of the base
    ID, device ID, and the status ID.  All of these arbitration ID's will
    include 8-bytes of data.  The specific decoding of the data is handled by
    the StatusXX() objects.  A bried description of the signals within the
    status frames are below:

        STATUS_01 : Faults, Limit Switch State, Output Percent
        STATUS_02 :
        STATUS_03 :
        STATUS_04 :
        STATUS_05 :
        STATUS_06 :
        STATUS_07 :
        STATUS_08 :
        STATUS_09 :
        STATUS_10 :
        STATUS_11 :
        STATUS_12 :
        STATUS_13 :
        STATUS_14 :
        STATUS_15 :


    Attributes
    ----------
    status01 : Status01 object
        Decode and store status 1

        ...
        ...
        ...

    status15 : Status01 object
        Decode and store status 15

    References
    ----------
    TODO: Add NI whitepaper or another CAN spec
    https://github.com/CrossTheRoadElec/Phoenix-netmf/blob/master/CTRE/LowLevel/MotController_LowLevel.cs

    """

    def __init__(self):
        """
        Constructor creates the status objects
        """

        self.status01 = Status01()


class Status01():
    """Decode and house CTRE TalonSRX/VictorSPX CAN bus STATUS_01 data frame

    Attributes
    ----------
    timestamp : float
        The time the data frame was received
    hardware_failure : int
        Generic hardware faults
    reverse_limit_switch : int

    forward_limit_switch : int

    under_voltage : int
        Not enough voltage being supplied
    reset_during_en : int

    sensor_out_of_phase : int

    sensor_overflow : int

    reverse_soft_limit : int

    forward_soft_limit : int

    hardware_esd_reset : int

    remote_loss_of_signal : int

    motor_output_percent : int

    fwd_limit_switch_closed : int

    rev_limit_switch_closed : int

    Methods
    -------
    DecodeData(data)
        Decodes the data frame and updates all of the attributes

    """

    def __init__(self):
        """
        Constructor initializes all of the attributes to null or 0 values
        """

        self.timestamp = 0.0
        self.hardware_failure = 0
        self.reverse_limit_switch = 0
        self.forward_limit_switch = 0
        self.under_voltage = 0
        self.reset_during_en = 0
        self.sensor_out_of_phase = 0
        self.sensor_overflow = 0
        self.reverse_soft_limit = 0
        self.forward_soft_limit = 0
        self.hardware_esd_reset = 0
        self.remote_loss_of_signal = 0
        self.motor_output_percent = 0.0
        self.fwd_limit_switch_closed = 0
        self.rev_limit_switch_closed = 0


    def DecodeData(self, data, timestamp):
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

        self.timestamp = timestamp
        self._GetFaults(data)
        self._GetMotorOutputPercent(data)
        self._GetFwdLimitSwitchClosed(data)
        self._GetRevLimitSwitchClosed(data)


    def _GetFaults(self, data):
        """
        Decodes and sets the motor controller motor faults.  See GetFaults for
        the CTRE implementation.

        Parameters
        ----------
        data : int
            An integer input of the 8-bytes of data

        """

        self.hardware_failure = (data) & 1
        self.reverse_limit_switch = ((data >> 1) & 1)
        self.forward_limit_switch = ((data >> 2) & 1)
        self.under_voltage = ((data >> 3) & 1)
        self.reset_during_en = ((data >> 4) & 1)
        self.sensor_out_of_phase = ((data >> 5) & 1)
        self.sensor_overflow = ((data >> 6) & 1)
        self.reverse_soft_limit = ((data >> (0x18)) & 1)
        self.forward_soft_limit = ((data >> (0x18 + 1)) & 1)
        self.hardware_esd_reset = ((data >> (0x18 + 2)) & 1)
        self.remote_loss_of_signal = ((data >> (0x30 + 4)) & 1)


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
        self.motor_output_percent = float(raw) / 1023.0


    def _GetFwdLimitSwitchClosed(self, data):
        """
        Decodes and sets the forward limit switch.  See IsFwdLimitSwitchClosed
        for the CTRE implementation.

        Parameters
        ----------
        data : int
            An integer input of the 8-bytes of data

        """

        self.fwd_limit_switch_closed = (data >> (0x18 + 7)) & 1


    def _GetRevLimitSwitchClosed(self, data):
        """
        Decodes and sets the reverse limit switch.  See IsRevLimitSwitchClosed
        for the CTRE implementation.

        Parameters
        ----------
        data : int
            An integer input of the 8-bytes of data

        """

        self.rev_limit_switch_closed = (data >> (0x18 + 6)) & 1


class Status02():
    """Decode and house CTRE TalonSRX/VictorSPX CAN bus STATUS_02 data frame

    Attributes
    ----------
    timestamp : float
        The time the data frame was received
    output_current : float
        The output current
    sensor_position : float

    sensor_velocity : float

    remote_loss_of_signal : int

    hardware_esd_reset : int

    reset_during_en : int

    sensor_out_of_phase : int
    
    sensor_overflow : int

    reverse_soft_limit : int

    forward_soft_limit : int

    reverse_limit_switch : int

    forward_limit_switch : int

    under_voltage : int


    Methods
    -------
    DecodeData(data)
        Decodes the data frame and updates all of the attributes

    """

    def __init__(self):
        """
        Constructor initializes all of the attributes to null or 0 values
        """

        self.timestamp = 0.0
        self.output_current = 0.0
        self.sensor_position = 0.0
        self.sensor_velocity = 0.0
        self.remote_loss_of_signal = 0
        self.hardware_esd_reset = 0
        self.reset_during_en = 0
        self.sensor_out_of_phase = 0
        self.sensor_overflow = 0
        self.reverse_soft_limit = 0
        self.forward_soft_limit = 0
        self.reverse_limit_switch = 0
        self.forward_limit_switch = 0
        self.under_voltage = 0

    def DecodeData(self, data, timestamp):
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

        self.timestamp = timestamp
        self._GetOutputCurrent(data)
        self._GetSensorPosition(data)
        self._GetSensorVelocity(data)
        self._GetStickyFaults(data)

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
        self.output_current = float(raw) * 0.125

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
        self.sensor_position = raw

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
        self.sensor_velocity = raw

    def _GetStickyFaults(self, data):
        """
        Decodes and sets the sticky faults.  See GetStickyFaults
        for the CTRE implementation.

        Parameters
        ----------
        data : int
            An integer input of the 8-bytes of data

        """

        self.remote_loss_of_signal = ((data >> (0x38 + 0)) & 1)
        self.hardware_esd_reset =    ((data >> (0x38 + 1)) & 1)
        self.reset_during_en =       ((data >> (0x38 + 2)) & 1)
        self.sensor_out_of_phase =   ((data >> (0x38 + 5)) & 1)
        self.sensor_overflow =       ((data >> (0x38 + 6)) & 1)
        self.reverse_soft_limit =    ((data >> (0x30 + 0)) & 1)
        self.forward_soft_limit =    ((data >> (0x30 + 1)) & 1)
        self.reverse_limit_switch =  ((data >> (0x30 + 2)) & 1)
        self.forward_limit_switch =  ((data >> (0x30 + 3)) & 1)
        self.under_voltage =         ((data >> (0x30 + 4)) & 1)
