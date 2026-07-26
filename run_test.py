#!/usr/bin/env python3
import os
import sys

# Add workspace to path
sys.path.insert(0, r'd:\Claude_VSCode_20260618\KCG\KoreaStrategyGroup')

# Clear env to test loading from file
os.environ.pop('GMAIL_USER', None)
os.environ.pop('GMAIL_APP_PASSWORD', None)

# Now change to workspace and import (will trigger _load_dotenv())
os.chdir(r'd:\Claude_VSCode_20260618\KCG\KoreaStrategyGroup')

# Import the module - this will call _load_dotenv() at module level
from ksg_procurement import main

# Now test main with --to example@example.com
print("=" * 60)
print("Testing ksg_procurement.py with .env loader fix")
print("=" * 60)
print(f"GMAIL_USER from env: {os.environ.get('GMAIL_USER', 'NOT SET')}")
print(f"GMAIL_APP_PASSWORD from env: {os.environ.get('GMAIL_APP_PASSWORD', 'NOT SET')}")
print()
print("Running: main(['--to', 'example@example.com'])")
print("-" * 60)
result = main(['--to', 'example@example.com'])
print("-" * 60)
print(f"Result code: {result}")
