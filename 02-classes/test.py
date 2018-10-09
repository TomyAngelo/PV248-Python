#!/usr/bin/python3
from scorelib import load
import sys

prints = load(sys.argv[1])
for key, item in prints.items():
    item.format()
    print("")
