#!/bin/python

import os

os.system("clear")
cwd = os.getcwd()
cwd = cwd.split("/")[-1]
os.system(f"(echo {cwd}; cat) | nc 127.0.0.1 4444") 
