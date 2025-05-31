# config/settings.py

import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'settings.yaml')

with open(CONFIG_PATH, 'r') as f:
    SETTINGS = yaml.safe_load(f)
