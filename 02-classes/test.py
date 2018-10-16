#!/usr/bin/python3
from scorelib import load
import sys

prints = load(sys.argv[1])
for item in sorted( prints, key=lambda item: item.print_id):
    item.format()
    print("")
