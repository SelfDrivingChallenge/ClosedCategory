# Sample code

In order to quickly get up to speed with the basics of controlling the kart, we provide some sample code to demonstrate how to control the motors and actuators on the kart. Additionally we provide a data recorder for recording camera footage alongside control inputs from the kart, and camera mappings to facilitate addressing the front, left and right cameras from software independently of the kart being used.

Current camera mappings are not definitive as the organization is still in the process of finalizing the setup of karts 2 and 3. Once available you can update them
by replacing the contents of the "configs" folder with an updated one. This should have no effect on your code.

Please note that these sample files only demonstrate very limited basic functionality, for further information about control messages and their structure please refer to the wiki.


## Brake Demo

The brake demo contains a generic function to initialize CAN-bus communication with the kart, using the USB to CAN interfaces available on the karts. In order to run this code without access to a physical CAN-bus it is possible to set up a virtual CAN-bus on Linux, and replacing "can0" in the initialization function with "vcan0".

The main function of the brake demo sets up a task to periodically send brake messages until stopped, and demonstrates how this task can be updated to move the
brake actuator to and from the 50% mark. Please note that a delay is used because the actuator takes time to extend to 50%. Sending a 0% message directly after would result in the action being cancelled as 0% is now the new target value.


## Motor Demo

The motor demo contains the same function for connecting to the CAN-bus as used in the brake demo, please refer to the brake demo section for further details.

The main function of the motor demo creates a task for periodically sending messages to the motor ECU until stopped, with the third byte of the message set to 0x01 (int value 1) in order to set the kart to forward drive. This task is then updated to accelerate the motor to full speed.


## Steer Demo

The steering demo contains the same function for connecting to the CAN-bus as used in the brake demo, please refer to the brake demo section for further details.

The main function of the steering demo creates a task for periodically sending messages to the steer ECU until stopped. This task is then updated by packing a float value of 0.3 into the first 4 bytes of the message, in order to steer to this position.


## Data Recorder

In order to maximize both the reusability of the codebase developed by the teams, and potentially recorded data in general, we provide a generic data recorder which
you can use to record data for testing purposes or for traning neural networks. This recorder saves timestamped images from all three cameras, along with a csv containing input to and feedback from the kart. You are free to either use this recorder as is, extend it to fit your purposes, or develop your own data recorder.

The data recorder uses a kart independed way of addressing the cameras, using kart specific configuration files, as is explained in the camera configuration section. It is recommended you use this method in your own solutions as we cannot guarantee you will be using the same kart throughout the challenge. The recorder does not capture lidar data, since the manner in which you record lidar data varies depending on the use case.


## Camera configuration

As mentioned, each kart is equipped with three cameras, facing forward, left and right respectively. In order to correctly identify the cameras in code independendly of the kart, we have written some example code (`video.py`).  
This code iterates of a set of configuration files until it finds a configuration where all paths used in the configuration exists. It the returns this configuration (or `None` if no configuration seems to be valid).  

_Note: It is highly recommended you use this method in your own solutions as we cannot guarantee you will be using the same kart throughout the challenge._