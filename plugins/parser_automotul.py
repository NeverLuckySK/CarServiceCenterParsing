from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from core.plugin_base import PluginBase
from core.models import ServiceItem


class AutoMotulPlugin(PluginBase):
    id = "33333333-3333-3333-3333-333333333333"
    name = "Auto-Motul"
    plugin_type = "Parser"
    author = "Copilot"
    version = "1.0"
    release_date = "2024-02-10"
    description = "Парсинг цен с auto-motul.ru"
    
    settings_schema = {
        "url": {"type": "str", "label": "URL источника", "default": "https://auto-motul.ru/price/"},
        "timeout": {"type": "int", "label": "Таймаут (сек)", "default": 15}
    }

    def load(self):
        url = self.settings.get("url", "https://auto-motul.ru/price/")
        timeout = int(self.settings.get("timeout", 15))

        # Allow requests to verify SSL certificates, but if it fails on your environment 
        # (some corporate proxies or specific setups), verify=False might be needed debugging.
        # For public sites, verify=True is standard.
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Network error: {e}")

        soup = BeautifulSoup(response.content, "html.parser")
        items = []

        # Find all category blocks
        categories = soup.find_all("div", class_="price-list-category")

        for cat_div in categories:
            # Extract category name
            cat_title_tag = cat_div.find("h3", class_="price-list-category__title")
            category_name = cat_title_tag.get_text(strip=True) if cat_title_tag else "Общее"

            # Find all service items in this category
            services = cat_div.find_all("li", class_="service-list-dish")

            for service in services:
                # Name extraction
                # The structure is: <li> <div> <div>NAME</div> ... </div> ... </li>
                
                # Find the wrapper div that contains the name and description
                wrapper_div = service.find("div")
                if not wrapper_div:
                    continue
                
                name_div = wrapper_div.find("div")
                if not name_div:
                    continue
                    
                name = name_div.get_text(strip=True)

                # Price extraction
                price_div = service.find("div", class_="service-list-dish__price")
                if not price_div:
                    continue

                price_text = price_div.get_text(strip=True)
                price_val = self._parse_price(price_text)

                # Only add if price is valid
                if price_val is not None:
                    items.append(ServiceItem(
                        name=name,
                        price=price_val,
                        category=category_name,
                        source="auto-motul.ru"
                    ))
        
        return items

    def _parse_price(self, text: str) -> float | None:
        # Example: "2 500 руб." -> 2500.0, "от 500" -> 500.0
        # Remove spaces
        text = text.replace("\xa0", "").replace(" ", "")
        
        # Simple extraction: keep digits. 
        # If range or complicate string, this might need regex.
        # Given "300 руб.", let's just strip non-digit chars but keep separators?
        
        # Better approach: find the first number.
        import re
        match = re.search(r"(\d+([.,]\d+)?)", text)
        if match:
            num_str = match.group(1).replace(",", ".")
            try:
                return float(num_str)
            except ValueError:
                return None
        return None


def get_plugin() -> PluginBase:
    return AutoMotulPlugin()
