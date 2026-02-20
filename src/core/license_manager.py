from __future__ import annotations

import json
from datetime import datetime, date
from pathlib import Path

class LicenseManager:
    def __init__(self, data_dir: Path):
        self._data_dir = data_dir
        self._db_file = data_dir / "licenses.json"
        
    def activate(self, key: str) -> bool:
        """
        Activates the given key if valid in licenses.json.
        Returns True if successful, False otherwise.
        """
        if not key or not key.strip():
            return False
            
        key = key.strip()

        # 1. Load DB
        if not self._db_file.exists():
            return False
            
        try:
            with open(self._db_file, 'r', encoding='utf-8') as f:
                db = json.load(f)
        except (json.JSONDecodeError, OSError):
            return False
            
        if not isinstance(db, list):
            return False
            
        # Helper method for validation
        def is_valid(lic: dict) -> bool:
            try:
                start_str = lic.get("start_date")
                end_str = lic.get("end_date")
                if not start_str or not end_str:
                    return False
                today = date.today()
                start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
                return start_date <= today <= end_date
            except (ValueError, TypeError):
                return False

        # 2. Check if key is valid
        found_lic = None
        for lic in db:
            if lic.get("key") == key:
                if is_valid(lic):
                    found_lic = lic
                break
        
        if not found_lic:
            return False
            
        # 3. Save active key to config
        config_file = self._data_dir / "active_key.txt"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(found_lic["key"])
        except OSError:
            return False
            
        return True

    def check_license(self) -> dict | None:
        """
        Checks currently active key.
        Returns license dict if valid, else None.
        """
        config_file = self._data_dir / "active_key.txt"
        active_key = None
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    active_key = f.read().strip()
            except OSError:
                pass
        
        if not active_key:
            return None
            
        # Check against DB
        if not self._db_file.exists():
            return None
            
        try:
            with open(self._db_file, 'r', encoding='utf-8') as f:
                db = json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
            
        if not isinstance(db, list):
            return None

        # Helper method for validation
        def is_valid(lic: dict) -> bool:
            try:
                start_str = lic.get("start_date")
                end_str = lic.get("end_date")
                if not start_str or not end_str:
                    return False
                today = date.today()
                start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
                return start_date <= today <= end_date
            except (ValueError, TypeError):
                return False

        for lic in db:
            if lic.get("key") == active_key:
                if is_valid(lic):
                    return lic
                return None
                
        return None

    def _is_valid(self, lic: dict) -> bool:
        """Deprecated: using internal helpers"""
        pass


    def get_status_text(self) -> str:
        lic = self.check_license()
        if lic:
            return f"{lic.get('owner', 'Unknown')} (до {lic.get('end_date')})"
        return "Free Version (Unregistered)"
