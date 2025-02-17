from time import sleep
import struct
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
    
    steer_message = can.Message(arbitration_id=0x220, data=[0, 0, 0, 0, 0, 0, 0, 0], is_extended_id=False)
    steer_task = bus.send_periodic(brake_message, CAN_MESSAGE_SENDING_SPEED)

    steer_message.data = list(bytearray(struct.pack("f", 0.3))) + [0]*4
    steer_message.modify_data(steer_message)
    
    sleep(2)

    steer_message.data = [0]*8
    steer_message.modify_data(steer_message)

    sleep(2)


if __name__ == '__main__':
    main()
