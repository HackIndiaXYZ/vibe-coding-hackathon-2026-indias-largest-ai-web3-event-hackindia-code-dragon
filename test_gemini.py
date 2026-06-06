#!/usr/bin/env python3
"""Quick test script for Gemini integration"""

import sys
sys.path.insert(0, '.')

from engine_gemini import GeminiInferenceEngine

print("🔧 Testing Gemini Inference Engine...")
print("=" * 50)

try:
    # Initialize engine
    engine = GeminiInferenceEngine()
    print("✅ Engine initialized successfully!\n")
    
    # Test message
    messages = [
        {"role": "user", "content": "Say hello as Ren AI in just one sentence."}
    ]
    
    print("📤 Sending test request...")
    response = engine.generate_response("ren", messages)
    
    print("\n✅ Response received:")
    print("-" * 50)
    print(response)
    print("-" * 50)
    print("\n✅ Gemini integration working perfectly!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check if FIREBASE_API_KEY is set in .env")
    print("2. Ensure google-generativeai is installed: pip install google-generativeai")
    print("3. Verify your Firebase project has Gemini API enabled")
    sys.exit(1)
