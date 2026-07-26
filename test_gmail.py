#!/usr/bin/env python3
import os
import subprocess
import sys

os.chdir(r'd:\Claude_VSCode_20260618\KCG\KoreaStrategyGroup')
os.environ['GMAIL_USER'] = 'biostar@ajou.ac.kr'
os.environ['GMAIL_APP_PASSWORD'] = 'nuwfoyepklgrixytx'

result = subprocess.run([sys.executable, 'ksg_procurement.py', '--to', 'example@example.com'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print("Return code:", result.returncode)
