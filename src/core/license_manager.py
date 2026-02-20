from __future__ import annotations

import json
from datetime import datetime, date
from pathlib import Path

class LicenseManager:
    def __init__(self, data_dir: Path):
        self._license_file = data_dir / "licenses.json"
        
    def check_license(self) -> dict | None:
        """
        Checks if a valid active license exists in licenses.json.
        Returns the license dict if valid, or None if no valid license found (Free version).
        """
        if not self._license_file.exists():
            return None
            
        try:
            with open(self._license_file, 'r', encoding='utf-8') as f:
                licenses = json.load(f)
                
            if not isinstance(licenses, list):
                return None
                
            today = date.today()
            
            for lic in licenses:
                # Expected format: 
                # {"key": "...", "owner": "...", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"}
                try:
                    start_str = lic.get("start_date")
                    end_str = lic.get("end_date")
                    
                    if not start_str or not end_str:
                        continue
                        
                    start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                    end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
                    
                    if start_date <= today <= end_date:
                        return lic
                except (ValueError, TypeError):
                    continue
                    
            return None
            
        except (json.JSONDecodeError, OSError):
            return None

    def get_status_text(self) -> str:
        lic = self.check_license()
        if lic:
            return f"Licat: {lic.get('owner', 'Unknown')} (до {lic.get('end_date')})"
        return "Free Version (Unregistered)"
