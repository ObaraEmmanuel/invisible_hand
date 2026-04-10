import os
import sys

from main import run

if hasattr(sys, "_MEIPASS"):
    os.chdir(sys._MEIPASS)

if __name__ == '__main__':
    run()
