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
    
    brake_message = can.Message(arbitration_id=0x110, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)
    brake_task = bus.send_periodic(brake_message, CAN_MESSAGE_SENDING_SPEED)
    
    brake_message.data = [50] + [0]*7
    brake_task.modify_data(brake_message)

    sleep(2)

    brake_message.data = [0]*8
    brake_task.modify_data(brake_message)

    sleep(2)


if __name__ == '__main__':
    main()