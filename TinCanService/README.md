# Introduction
The TinCan Service is required to communicate with the USBTin CAN Adapter on the karts.

# Installation

- Make sure `can-utils` is installed before starting the installation;
- Ensure that both `install.sh` and `tinSocketCan.sh` are executable (or make them executable using `chmod +x *.sh` in this directory);
- Run `install.sh` from this directory.

# Verifying Installation
After installation, there should be a systemd service called `tinCan.Service`, which becomes active when you connect a TinCan and becomes inactive when you disconnect it from the machine.  
You can easily check this with `systemctl status tinCan` or via Cockpit (if installed).

# Bugs
It is not possible to connect more than one TinCan with this solution.