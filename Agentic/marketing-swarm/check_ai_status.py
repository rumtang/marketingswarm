#!/usr/bin/env python3
"""
Check AI Integration Status
Quick script to verify AI setup and configuration
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))


def check_ai_status():
    """Check and display AI integration status"""
    
    print("🔍 AI Integration Status Check")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Check environment variables
    print("\n📋 Environment Configuration:")
    
    configs = {
        "USE_AI_RESPONSES": os.getenv("USE_AI_RESPONSES", "false"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "not_set"),
        "AI_MODEL": os.getenv("AI_MODEL", "gpt-4"),
        "AI_DEFAULT_TEMPERATURE": os.getenv("AI_DEFAULT_TEMPERATURE", "0.7"),
        "AI_MAX_TOKENS": os.getenv("AI_MAX_TOKENS", "300"),
        "MOCK_API_RESPONSES": os.getenv("MOCK_API_RESPONSES", "false"),
    }
    
    for key, value in configs.items():
        if key == "OPENAI_API_KEY":
            if value != "not_set" and not value.startswith("sk-mock"):
                display_value = f"{value[:7]}...{value[-4:]}" if len(value) > 11 else "***"
                status = "✅"
            elif value.startswith("sk-mock"):
                display_value = value
                status = "🧪"  # Test mode
            else:
                display_value = "❌ Not configured"
                status = "❌"
        else:
            display_value = value
            status = "✅" if value != "not_set" else "❌"
        
        print(f"{status} {key}: {display_value}")
    
    # Check if AI is properly configured
    print("\n🤖 AI Status:")
    
    ai_enabled = configs["USE_AI_RESPONSES"].lower() == "true"
    has_api_key = configs["OPENAI_API_KEY"] != "not_set"
    is_mock = configs["MOCK_API_RESPONSES"].lower() == "true"
    
    if ai_enabled and has_api_key and not is_mock:
        print("✅ AI is ENABLED and configured for production")
    elif ai_enabled and is_mock:
        print("🧪 AI is ENABLED in TEST MODE (using mocks)")
    elif ai_enabled and not has_api_key:
        print("⚠️  AI is ENABLED but NO API KEY configured")
    else:
        print("🔴 AI is DISABLED (using predetermined responses)")
    
    # Test imports
    print("\n📦 Module Import Test:")
    try:
        from ai.response_generator import ai_generator
        print("✅ ai.response_generator imported successfully")
    except Exception as e:
        print(f"❌ Failed to import ai.response_generator: {e}")
    
    try:
        from ai.context_manager import context_manager
        print("✅ ai.context_manager imported successfully")
    except Exception as e:
        print(f"❌ Failed to import ai.context_manager: {e}")
    
    try:
        from ai.prompts import build_agent_system_prompt
        print("✅ ai.prompts imported successfully")
    except Exception as e:
        print(f"❌ Failed to import ai.prompts: {e}")
    
    # Check OpenAI package
    print("\n📚 Dependencies:")
    try:
        import openai
        print(f"✅ OpenAI package installed (version: {openai.__version__})")
    except ImportError:
        print("❌ OpenAI package not installed. Run: pip install openai==1.12.0")
    
    # Recommendations
    print("\n💡 Recommendations:")
    
    if not ai_enabled:
        print("- Set USE_AI_RESPONSES=true to enable AI")
    
    if not has_api_key:
        print("- Add your OpenAI API key to .env file")
        print("  OPENAI_API_KEY=sk-your-actual-key-here")
    
    if is_mock and ai_enabled:
        print("- Set MOCK_API_RESPONSES=false for production")
    
    if ai_enabled and has_api_key and not is_mock:
        print("- System is ready for AI-powered responses!")
        print("- Monitor costs with AI_DAILY_TOKEN_LIMIT")
        print("- Adjust AI_DEFAULT_TEMPERATURE for variety")
    
    print("\n✨ Run 'python demo_ai_integration.py' to see AI in action!")


if __name__ == "__main__":
    check_ai_status()