#!/usr/bin/env python
import sys
from pathlib import Path
import traceback

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root / 'src'))

try:
    from ide import GuaraniIDE
    print("✓ Import successful")
    
    # Try to create IDE without mainloop
    ide = GuaraniIDE()
    print("✓ IDE initialization successful")
    ide.quit()
    print("✓ IDE closed successfully")
except Exception as e:
    print(f"✗ Error: {e}")
    traceback.print_exc()
