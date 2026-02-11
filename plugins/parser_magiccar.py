from __future__ import annotations

import re
import requests
from bs4 import BeautifulSoup
from core.plugin_base import PluginBase
from core.models import ServiceItem


class MagicCarParser(PluginBase):
    id = "550e8400-e29b-41d4-a716-446655449999"
    name = "Magic Car 24"
    plugin_type = "Source"
    author = "Copilot"
    version = "1.0.0"
    description = "Парсер услуг с сайта magic-car24.ru"
    
    settings_schema = {
        "url": {
            "type": "str",
            "label": "URL сайта",
            "default": "https://magic-car24.ru/"
        },
        "default_category": {
            "type": "str",
            "label": "Категория по умолчанию",
            "default": "Прайс-лист"
        }
    }

    def load(self) -> list[ServiceItem]:
        url = self.settings.get("url", "https://magic-car24.ru/")
        default_category = self.settings.get("default_category", "Прайс-лист")
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
        except Exception as e:
            # We log error or print it, but for plugin return empty list is safer than crash
            print(f"Error fetching {url}: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        items = []

        # The prices are located in a specific block with class 't022__text'
        price_blocks = soup.find_all('div', class_='t022__text')

        for block in price_blocks:
            paragraphs = block.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if not text:
                    continue

                # Regex to find "Service - from Price" pattern
                # Example: "Замена порога кузова - от 22 000р"
                # OR: "Покраска капота от - 18 000р"
                
                # Covers both " - от " and " от - "
                match = re.search(r'(.*?)\s*[\-–—]?\s*от\s*[\-–—]?\s*([\d\s]+)р', text, re.IGNORECASE)

                if match:
                    name = match.group(1).strip()
                    price_str = match.group(2).replace(' ', '').replace('\xa0', '')
                    
                    try:
                        price = float(price_str)
                    except ValueError:
                        continue
                        
                    items.append(ServiceItem(
                        name=name,
                        price=price,
                        category=default_category,
                        source="magic-car24.ru",
                        url=url
                    ))
        
        return items

def register():
    """Factory function to register the plugin."""
    return MagicCarParser()
