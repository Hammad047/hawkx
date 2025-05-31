from pathlib import Path

# Create the content for config/loader.py again after state reset
loader_code = """
import yaml
import os

def load_config(path='config/settings.yaml'):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, 'r') as f:
        return yaml.safe_load(f)
"""

# Create the directory and file
config_dir = Path("hawkx/config")
config_dir.mkdir(parents=True, exist_ok=True)
loader_file = config_dir / "loader.py"
loader_file.write_text(loader_code)

loader_file.resolve()
