from pathlib import Path
import sys

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root / 'src'))

from ide import GuaraniIDE

if __name__ == '__main__':
    GuaraniIDE().mainloop()
