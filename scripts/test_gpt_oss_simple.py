#!/usr/bin/env python3
"""
Simple test of gpt-oss model response time and quality
"""

import subprocess
import time

prompt = """You are an expert game developer. In 100 words or less, explain how to implement vector memory for game AI agents.

Focus on:
1. What is vector memory
2. How agents can use it
3. One code example

Be concise and practical."""

print("🤖 Testing gpt-oss:20b with simple prompt...")
print(f"📝 Prompt: {len(prompt)} characters")
print("-" * 60)

start_time = time.time()

try:
    result = subprocess.run(
        ["ollama", "run", "gpt-oss:20b", prompt],
        capture_output=True,
        text=True,
        timeout=300
    )
    
    elapsed = time.time() - start_time
    
    if result.returncode == 0:
        print("✅ Success!")
        print(f"⏱️ Time: {elapsed:.1f} seconds")
        print(f"📏 Output length: {len(result.stdout)} characters")
        print("-" * 60)
        print(result.stdout)
        print("-" * 60)
    else:
        print(f"❌ Error: {result.stderr}")
        
except subprocess.TimeoutExpired:
    print("⏱️ Timed out after 5 minutes")
except Exception as e:
    print(f"❌ Exception: {e}")