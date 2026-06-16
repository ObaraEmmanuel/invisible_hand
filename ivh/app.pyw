import os
import sys

if hasattr(sys, "_MEIPASS"):
    os.chdir(sys._MEIPASS)

root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from ivh.main import run

if __name__ == '__main__':
    run()
