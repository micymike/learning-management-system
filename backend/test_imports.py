#!/usr/bin/env python3
"""Test script to verify imports are working"""

try:
    import asyncio
    print("[OK] asyncio imported successfully")
except Exception as e:
    print(f"[ERROR] asyncio import failed: {e}")

try:
    from flask import Flask
    print("[OK] Flask imported successfully")
except Exception as e:
    print(f"[ERROR] Flask import failed: {e}")

try:
    import openai
    print("[OK] OpenAI imported successfully")
except Exception as e:
    print(f"[ERROR] OpenAI import failed: {e}")

print("Import test completed")