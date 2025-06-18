"""
OpenAI helper to handle both real and mock clients
"""

import os
from typing import Union

def get_openai_client():
    """Get OpenAI client (real or mock based on configuration)"""
    from utils.mock_openai import should_use_mock, MockOpenAI
    
    if should_use_mock():
        return MockOpenAI(api_key=os.getenv("OPENAI_API_KEY", "sk-mock"))
    else:
        from openai import OpenAI
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))