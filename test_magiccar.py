import sys
import os

# Ensure src is in python path
current_dir = os.getcwd()
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from plugins.parser_magiccar import MagicCarParser

def test_parser():
    parser = MagicCarParser()
    print(f"Testing plugin: {parser.name}")
    
    # Simulate loading settings (usually handled by UI/Base init)
    # The base init reads defaults from schema, so we can override if needed
    parser.settings["url"] = "https://magic-car24.ru/"
    
    try:
        results = parser.load()
        print(f"Found {len(results)} services.")
        for item in results:
            # item is ServiceItem dataclass
            print(f"- {item.name}: {item.price} ({item.category})")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parser()
