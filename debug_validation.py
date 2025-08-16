#!/usr/bin/env python3
"""Debug the exact validation flow to find where the dict is coming from"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sefas.agents.checkers import LogicChecker

# Create a checker
test_config = {
    'role': 'Logic Validation Engine',
    'model': 'gpt-4o-mini', 
    'temperature': 0.1,
    'provider': 'openai'
}

checker = LogicChecker(test_config)

# Test the specific failing case
test_dict = {
    'proposal': 'RNA world hypothesis suggests early life. Rating: 7.2. Logic: sound reasoning',
    'reasoning': 'Based on experimental evidence'
}

print("🔍 Debugging _extract_confidence call")
print(f"Input type: {type(test_dict)}")
print(f"Input content: {test_dict}")

try:
    # This is exactly what failed in our test
    result = checker._extract_confidence(test_dict)
    print(f"✅ Success: {result}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
    # Let's trace through the method manually
    print("\n🔧 Manual method execution:")
    
    # Check if it's a dict
    if isinstance(test_dict, dict):
        print("✅ Detected as dict")
        
        # Check for string content
        for key in ['content', 'proposal', 'analysis', 'text', 'response', 'description']:
            if key in test_dict and isinstance(test_dict[key], str):
                text_str = test_dict[key]
                print(f"✅ Found string content in '{key}': {text_str}")
                break
        else:
            print("❌ No string content found, would use str(dict)")
            text_str = str(test_dict)
    
    print(f"Text to process: {text_str}")
    print(f"Type: {type(text_str)}")
    
    # Now try the regex
    import re
    patterns = [
        r'confidence[:\s]+([0-9.]+)',
        r'([0-9.]+)\s*confidence',
    ]
    
    for pattern in patterns:
        try:
            match = re.search(pattern, text_str.lower())
            if match:
                print(f"✅ Pattern matched: {pattern} -> {match.group(1)}")
                break
        except Exception as pattern_error:
            print(f"❌ Pattern failed: {pattern} -> {pattern_error}")