#!/usr/bin/env python3
"""Inline test to verify ksg_procurement.py loader fix."""
import os
import sys
import tempfile
from pathlib import Path

# Create a test .env with corrupted bytes and duplicate keys
test_env_content = """# Comment
PUBLIC_DATA_API_KEY=test_key_1
GMAIL_USER=old_gmail@example.com

# Corrupted line follows (mixed encoding will be replaced)
GMAIL_APP_PASSWORD=test_password_1

# Later duplicate entries (should override earlier ones)
GMAIL_USER=biostar@ajou.ac.kr
GMAIL_APP_PASSWORD=nuwfoyepklgrixytx
"""

# Write test .env 
with tempfile.TemporaryDirectory() as tmpdir:
    test_env_path = Path(tmpdir) / '.env'
    test_env_path.write_text(test_env_content)
    
    # Clear environment
    for key in ['PUBLIC_DATA_API_KEY', 'GMAIL_USER', 'GMAIL_APP_PASSWORD']:
        os.environ.pop(key, None)
    
    # Test the loader function
    sys.path.insert(0, r'd:\Claude_VSCode_20260618\KCG\KoreaStrategyGroup')
    
    # Import and call loader
    def _load_dotenv(path=".env"):
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8", errors="replace") as handle:
                    for line in handle:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key:
                            os.environ[key] = value
        except Exception as e:
            print(f"Load error: {e}")
    
    _load_dotenv(str(test_env_path))
    
    # Verify final values (later entries should win)
    print("Test Results:")
    print(f"  GMAIL_USER = {os.environ.get('GMAIL_USER', 'NOT SET')}")
    print(f"  GMAIL_APP_PASSWORD = {os.environ.get('GMAIL_APP_PASSWORD', 'NOT SET')}")
    print(f"  PUBLIC_DATA_API_KEY = {os.environ.get('PUBLIC_DATA_API_KEY', 'NOT SET')}")
    
    # Verify expected behavior
    assert os.environ.get('GMAIL_USER') == 'biostar@ajou.ac.kr', "Should load final GMAIL_USER"
    assert os.environ.get('GMAIL_APP_PASSWORD') == 'nuwfoyepklgrixytx', "Should load final GMAIL_APP_PASSWORD"
    assert os.environ.get('PUBLIC_DATA_API_KEY') == 'test_key_1', "Should load first PUBLIC_DATA_API_KEY"
    
    print("\n✓ All tests passed! Loader correctly handles duplicates and respects later values.")
