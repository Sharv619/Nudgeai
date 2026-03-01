#!/usr/bin/env python3
"""
Quick ElevenLabs Setup - Just enter your API key and you're done!
"""

# Step 1: Get API key from https://elevenlabs.io/api
# Step 2: Run this script
# Step 3: Enter your API key when prompted

import os
from pathlib import Path

print("🎙️ ElevenLabs Quick Setup")
print("=" * 30)
print("Get your free API key at: https://elevenlabs.io/api")
print()

api_key = input("Enter your ElevenLabs API Key: ").strip()

if not api_key:
    print("❌ No API key entered!")
else:
    # Save to .env
    env_file = Path(".env")

    if env_file.exists():
        with open(env_file, "a") as f:
            f.write(f"\nELEVENLABS_API_KEY={api_key}\n")
    else:
        with open(env_file, "w") as f:
            f.write(f"ELEVENLABS_API_KEY={api_key}\n")

    print("✅ Done! API key saved to .env file")
    print()
    print("To test, install elevenlabs package:")
    print("  pip install elevenlabs")
