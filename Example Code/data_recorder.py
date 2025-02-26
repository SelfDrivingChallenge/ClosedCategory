#/usr/bin/env python3

import sys
import cv2
import video
import can
import os
import threading
import time
import struct
from datetime import datetime
from collections import namedtuple
from typing import Optional, Dict, List, Literal, Tuple
from queue import Queue

class CanListener:
    """
    A can listener that listens for specific messages and stores their latest values.
    """

    _id_conversion = {
        0x110: 'brake',
        0x220: 'steering',
        0x330: 'throttle',
        0x1e5: 'steering_sensor'
    }

    def __init__(self, bus: can.Bus):
        self.bus = bus
        self.thread = threading.Thread(target = self._listen, args = (), daemon = True)
        self.running = False
        self.data : Dict[str, List[int]] = {name: None for name in self._id_conversion.values()}
    
    def start_listening(self):
        self.running = True
        self.thread.start()
    
    def stop_listening(self):
        self.running = False
    
    def get_new_values(self):
        values = self.data
        return values

    def _listen(self):
        while self.running:
            message: Optional[can.Message] = self.bus.recv(.5)
            if message and message.arbitration_id in self._id_conversion:
                self.data[self._id_conversion[message.arbitration_id]] = message.data

class ImageWorker:
    """
    A worker that writes images to disk.
    """

    def __init__(self, image_queue: Queue, folder: str):
        self.queue = image_queue
        self.thread = threading.Thread(target = self._process, args = (), daemon = True)
        self.folder: str = folder
    
    def start(self):
        self.thread.start()
    
    def stop(self):
        self.queue.join()

    def put(self, data):
        self.queue.put(data)
        
    def _process(self):
        while True:
            filename, image_type, image = self.queue.get()
            cv2.imwrite(os.path.join(self.folder, image_type, f'{filename}.png'), image)
            self.queue.task_done()

class CanWorker:
    """
    A worker that writes can-message values to disk.
    """

    def __init__(self, can_queue: Queue, folder: str):
        self.queue = can_queue
        self.thread = threading.Thread(target = self._process, args = (), daemon = True)
        self.folder_name = folder
        self.file_pointer = open(os.path.join(self.folder_name, f'recording.csv'), 'w')
        print('Timestamp|Steering|SteeringSpeed|Throttle|Brake|SteeringSensor', file = self.file_pointer)
    
    def start(self):
        self.thread.start()
    
    def stop(self):
        self.queue.join()
        self.file_pointer.close()
    
    def put(self, data):
        self.queue.put(data)
    
    def _process(self):
        while True:
            timestamp, values = self.queue.get()
            steering = str(struct.unpack("f", bytearray(values["steering"][:4]))[0]) if values["steering"] else ""
            steering_speed = str(struct.unpack(">I", bytearray(values["steering"][4:]))[0]) if values["steering"] else ""
            throttle = str(values["throttle"][0]/100) if values["throttle"] else ""
            brake = str(values["brake"][0]/100) if values["brake"] else ""
            if values["steering_sensor"]:
                steering_sensor = (values["steering_sensor"][1] << 8 | values["steering_sensor"][2])
                steering_sensor -= 65536 if steering_sensor > 32767 else 0
            else:
                steering_sensor = ""
            print(f'{timestamp}|{steering}|{steering_speed}|{throttle}|{brake}|{steering_sensor}', file=self.file_pointer)
            self.queue.task_done()


def main():
    print('Initializing...', file=sys.stderr)
    bus = initialize_can()
    cameras = initialize_cameras()

    print('Creating folders...', file=sys.stderr)
    recording_folder = "recording " + datetime.now().strftime("%d-%m-%Y %H-%M-%S")
    if not os.path.exists(recording_folder):
        os.mkdir(recording_folder)
        for subdir in cameras.keys():
            os.mkdir(os.path.join(recording_folder, subdir))

    can_listener = CanListener(bus)
    can_listener.start_listening()
    image_queue = Queue()
    image_worker = ImageWorker(image_queue, recording_folder)
    ImageWorker(image_queue, recording_folder).start()
    ImageWorker(image_queue, recording_folder).start()
    image_worker.start()
    can_worker = CanWorker(Queue(), recording_folder)
    can_worker.start()

    print('Recording...', file=sys.stderr)
    frames: Dict[str, cv2.Mat] = dict()
    try:
        while True:
            ok_count = 0
            values = can_listener.get_new_values()
            timestamp = time.time()
            for side, camera in cameras.items():
                ok, frames[side] = camera.retrieve()
                ok_count += ok
            if ok_count == len(cameras):
                for side, frame in frames.items():
                    image_worker.put((timestamp, side, frame))
                can_worker.put((timestamp, values))
            for camera in cameras.values():
                camera.grab()
    except KeyboardInterrupt:
        pass
    
    print('Stopping...', file=sys.stderr)
    can_listener.stop_listening()
    for camera in cameras.values():
        camera.release()
    image_worker.stop()
    can_worker.stop()


def initialize_can() -> can.Bus:
    """
    Set up the can bus interface and apply filters for the messages we're interested in.
    """
    bus = can.Bus(interface='socketcan', channel='can0', bitrate=500000)
    bus.set_filters([
        {'can_id': 0x110, 'can_mask': 0xfff, 'extended': False}, # Steering
        {'can_id': 0x220, 'can_mask': 0xfff, 'extended': False}, # Throttle
        {'can_id': 0x330, 'can_mask': 0xfff, 'extended': False}, # Brake
        {'can_id': 0x1e5, 'can_mask': 0xfff, 'extended': False}, # Steering sensor
    ])
    return bus

def initialize_cameras() -> Dict[str, cv2.VideoCapture]:
    """
    Initialize the opencv camera capture devices.
    """
    config: video.CamConfig = video.get_camera_config()
    if not config:
        print('No valid video configuration found!', file=sys.stderr)
        exit(1)
    cameras: Dict[str, cv2.VideoCapture] = dict()
    for camera_type, path in config.items():
        capture = cv2.VideoCapture(path)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 848)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        capture.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        capture.set(cv2.CAP_PROP_FOCUS, 0)
        capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) #important to set right codec to enable 60fps
        capture.set(cv2.CAP_PROP_FPS, 30) #make 60 to enable 60FPS
        cameras[camera_type] = capture
    return cameras

if __name__ == '__main__':
    main()