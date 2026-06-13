from pathlib import Path
import sys

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root / 'src'))

from main import main as guarani_main

if __name__ == '__main__':
    guarani_main()
