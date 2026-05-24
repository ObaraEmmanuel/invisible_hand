"""Flashing utility entry point"""

import sys
from esptool import main as esptool_main

if __name__ == '__main__':
    try:
        esptool_main(sys.argv[1:])
    except Exception as e:
        print(e)
        sys.exit(1)

