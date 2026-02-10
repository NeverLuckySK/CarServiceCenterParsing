# Архитектура

## Общая схема

```mermaid
graph TD
  UI[PyQt UI] -->|команды| AGG[Aggregator]
  UI -->|загрузка| LOADER[Plugin Loader]
  LOADER -->|модули| PLUGINS[Plugins]
  AGG -->|данные| UI
  PLUGINS -->|ServiceItem[]| AGG
```

## Модель плагина

```mermaid
classDiagram
  class PluginBase {
    +name: str
    +version: str
    +description: str
    +load() ServiceItem[]
  }
  class ServiceItem {
    +name: str
    +price: float
    +category: Optional[str]
    +source: str
  }
  PluginBase --> ServiceItem
```
