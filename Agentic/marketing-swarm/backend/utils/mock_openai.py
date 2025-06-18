"""
Mock OpenAI client for testing without API key
"""

class MockModels:
    """Mock models endpoint"""
    def list(self):
        return type('obj', (object,), {
            'data': [
                {'id': 'gpt-4', 'object': 'model'},
                {'id': 'gpt-3.5-turbo', 'object': 'model'}
            ]
        })

class MockChat:
    """Mock chat completions"""
    class Completions:
        async def create(self, **kwargs):
            # Return mock response based on input
            messages = kwargs.get('messages', [])
            if messages and 'robo-advisor' in str(messages).lower():
                content = "To launch a robo-advisor, focus on trust-building through transparent fee structures and educational content."
            else:
                content = "This is a mock response for testing purposes."
            
            return type('obj', (object,), {
                'choices': [{
                    'message': {
                        'content': content,
                        'role': 'assistant'
                    }
                }]
            })
    
    def __init__(self):
        self.completions = self.Completions()

class MockOpenAI:
    """Mock OpenAI client"""
    def __init__(self, api_key=None):
        self.api_key = api_key or "mock-key"
        self.models = MockModels()
        self.chat = MockChat()

# Helper to check if we should use mock
def should_use_mock():
    """Check if we should use mock OpenAI client"""
    import os
    return (
        os.getenv("MOCK_API_RESPONSES", "false").lower() == "true" or
        os.getenv("DEV_MODE", "false").lower() == "true" or
        os.getenv("OPENAI_API_KEY", "").startswith("sk-mock")
    )