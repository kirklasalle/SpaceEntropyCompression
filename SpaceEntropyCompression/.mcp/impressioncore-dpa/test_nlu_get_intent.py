


"""
Test NLU get_intent tool for ImpressionCore DPA

Created: 2024-10-15
Updated: 2025-07-26
Author: ImpressionCore Team
"""
import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from nlu_bridge import DPANLUBridge

if __name__ == "__main__":
    bridge = DPANLUBridge()
    test_text = "Remind me to call John at 5pm"
    intent = bridge.get_intent(test_text)
    print(f"Input: {test_text}")
    print(f"Extracted intent: {intent}")
    bridge.shutdown()
