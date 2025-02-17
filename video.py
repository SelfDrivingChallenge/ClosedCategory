import json
import os
import glob
from typing import TypedDict, Optional

class CamConfig(TypedDict):
    front: str
    left: str
    right: str

def get_camera_config(config_folder: str = "configs") -> Optional[CamConfig]:
    """
    Select a valid camera configuration from the config_folder and return it.
    
    Returns None if no valid configuration could be found.
    """
    for filename in glob.glob(os.path.join(os.path.normpath(config_folder), '*.json')):
        with open(filename, 'r') as fp:
            config: CamConfig = json.load(fp)
            if all((os.path.exists(camera) and not os.path.isdir(camera) for camera in config.values())):
                return config
    return None