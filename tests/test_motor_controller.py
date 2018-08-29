from src.decoder.motor_controller import MotorControllerCANStatus

# Test Faults
def test_GetFaults():
    motor_controller_can_status = MotorControllerCANStatus()
    motor_controller_can_status._GetFaults(1)
    assert motor_controller_can_status.status1['hardware_failure'] == 1
