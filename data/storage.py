# HawkX/data/storage.py

from pathlib import Path
import pandas as pd
import json
from datetime import datetime

class DataStorage:
    def __init__(self, base_dir='data/storage'):
        self.base_path = Path(base_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_trade_log_csv(self, data: dict, filename='trades_log.csv'):
        file_path = self.base_path / filename
        df = pd.DataFrame([data])

        if file_path.exists():
            df.to_csv(file_path, mode='a', header=False, index=False)
        else:
            df.to_csv(file_path, mode='w', header=True, index=False)

        return str(file_path)

    def save_signal_json(self, data: dict, filename='last_signal.json'):
        """
        Save the latest signal or strategy state to a JSON file.
        """
        file_path = self.base_path / filename
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4, default=str)

    def load_signal_json(self, filename='last_signal.json'):
        """
        Load previously saved signal or strategy state.
        """
        file_path = self.base_path / filename
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}

    # === Future Enhancements ===
    # def save_to_sqlite(self, table_name, data_dict): ...
    # def upload_to_s3(self, filename): ...
    # def enable_auto_pruning(self, retention_days): ...
