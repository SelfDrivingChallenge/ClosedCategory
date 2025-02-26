from time import sleep
import can


CAN_MESSAGE_SENDING_SPEED = 0.04


def initialize_can():
    """
    Set up the can bus interface
    """
    bus = can.Bus(interface='socketcan', channel='can0', bitrate=500000)
    return bus
    
    
def main():
    bus = initialize_can()
    
    motor_message = can.Message(arbitration_id=0x330, data=[0, 0, 1, 0, 0, 0, 0, 0], is_extended_id=False)
    motor_task = bus.send_periodic(motor_message, CAN_MESSAGE_SENDING_SPEED)
    
    sleep(2)
    
    motor_message.data = [100, 0, 1, 0, 0, 0, 0, 0]
    motor_task.modify_data(motor_message)
    
    sleep(2)



if __name__ == '__main__':
    main()
