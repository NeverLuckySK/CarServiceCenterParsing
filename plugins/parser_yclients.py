from __future__ import annotations

import re
import requests
import uuid
from typing import Any
from core.plugin_base import PluginBase, PluginType
from core.models import ServiceItem

class YClientsParser(PluginBase):
    def __init__(self):
        super().__init__()
        self._metadata = {
            "guid": "550e8400-e29b-41d4-a716-446655440002",
            "name": "YClients Parser",
            "type": PluginType.SOURCE,
            "version": "1.0.0",
            "author": "GitHub Copilot",
            "description": "Парсер для виджетов YClients (требуется Company ID)"
        }
        self.settings_schema = {
            "company_id": {
                "type": "str",
                "label": "ID Компании (Company ID)",
                "default": "1343757"
            },
            "auth_token": {
                "type": "str",
                "label": "Token (если требуется, Bearer ...)",
                "default": ""
            }
        }

    def load(self, settings: dict) -> list[dict]:
        company_id = settings.get("company_id", "1343757").strip()
        auth_token = settings.get("auth_token", "").strip()
        
        # Determine endpoints to try
        # 1. New Booking Form API (often uses a different host or path)
        # 2. Public API v1
        
        api_url = f"https://api.yclients.com/api/v1/company/{company_id}/services"
        
        headers = {
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Compatible; CarServiceParser/1.0)",
        }
        
        if auth_token:
            headers["Authorization"] = auth_token
        else:
            # Try a common guest token pattern or just omitting it
            # Many widgets use "Bearer Partner <key>" or just "Bearer <guest_token>"
            # Without a token, this usually returns 401. 
            pass

        services = []
        
        try:
            # Try services endpoint
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Expected format: {"data": [...services...], ...} or direct list
                items = data.get("data", []) if isinstance(data, dict) else data
                
                for item in items:
                    # item structure varies but usually has 'title', 'price_min', 'category_id'
                    name = item.get("title", "Unnamed Service")
                    price = float(item.get("price_min", 0))
                    category = item.get("category_id", "General") # ID, usually need separate call for category names
                    
                    services.append({
                        'category': str(category),
                        'service_name': name,
                        'price': price,
                        'source': "YClients",
                        'url': f"https://n1487850.yclients.com/company/{company_id}/personal/select-services?o="
                    })
            
            elif response.status_code == 401:
                print(f"YClients: Unauthorized. Please provide a valid Bearer token in settings.")
                # We could try to scrape the HTML if API fails, but it's an SPA.
                # Adding a dummy item to inform user
                if not services:
                     return []

        except Exception as e:
            print(f"YClients Error: {e}")
            
        return services

    def process(self, data: list[dict], settings: dict) -> list[dict]:
        return data

def register():
    return YClientsParser()
