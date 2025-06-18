"""
Mock OpenAI client for testing without API key
"""

import asyncio

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
        def create(self, **kwargs):
            """Synchronous create for compatibility"""
            return self._generate_mock_response(**kwargs)
        
        async def create(self, **kwargs):
            """Async create for compatibility"""
            return self._generate_mock_response(**kwargs)
        
        def _generate_mock_response(self, **kwargs):
            """Generate mock response based on input"""
            import random
            
            messages = kwargs.get('messages', [])
            temperature = kwargs.get('temperature', 0.7)
            
            # Extract context from messages
            system_content = ""
            user_content = ""
            
            for msg in messages:
                if msg.get('role') == 'system':
                    system_content = msg.get('content', '')
                elif msg.get('role') == 'user':
                    user_content = msg.get('content', '')
            
            # Generate personality-aware mock responses
            if 'sarah' in system_content.lower():
                responses = [
                    "From a strategic brand perspective, we need to focus on differentiation through trust and transparency.",
                    "Building on that point, brand equity requires consistent messaging across all touchpoints.",
                    "[interrupting] Wait, we're missing the bigger picture here - what's our emotional value proposition?"
                ]
            elif 'marcus' in system_content.lower():
                responses = [
                    "Let me stop you there - the data shows CAC is 40% above target. We need performance optimization now.",
                    "Looking at the metrics, our ROAS across channels averages 2.3x, but Google Search hits 4.1x.",
                    "I disagree. Without proper attribution modeling, we're flying blind on budget allocation."
                ]
            elif 'elena' in system_content.lower():
                responses = [
                    "This is exactly why we need disruptive content - standing out requires creative courage.",
                    "What if we flip the narrative entirely? Make saving money feel rebellious, not responsible.",
                    "Building on the creative angle, storytelling beats statistics every time in engagement metrics."
                ]
            elif 'david' in system_content.lower():
                responses = [
                    "From a UX perspective, reducing friction is our fastest path to conversion improvement.",
                    "User research indicates 73% abandon during onboarding - that's our real problem.",
                    "I'm concerned about the user journey here. Complexity kills conversion."
                ]
            elif 'priya' in system_content.lower():
                responses = [
                    "The statistical significance isn't there. We need 2,400 more samples for 95% confidence.",
                    "Correlation doesn't imply causation. Let's design a proper A/B test framework.",
                    "Data reveals interesting segmentation: mobile CAC is 3.2x desktop. That's actionable."
                ]
            elif 'alex' in system_content.lower():
                responses = [
                    "While you're debating, three competitors just launched. Speed beats perfection in growth.",
                    "Controversial take: what if we 10x the risk for 100x the reward? Go viral or go home.",
                    "Growth hacking opportunity: gamification increased Robinhood's activation 340%."
                ]
            else:
                responses = [
                    "This is a mock AI response demonstrating dynamic content generation.",
                    "Based on the context, here's a thoughtful analysis of the situation.",
                    "Considering multiple perspectives, the optimal approach would be..."
                ]
            
            # Add variety based on temperature
            if temperature > 0.7:
                responses.append("[thinking outside the box] What if we completely reimagined this approach?")
            
            # Return mock response object
            return type('obj', (object,), {
                'choices': [{
                    'message': {
                        'content': random.choice(responses),
                        'role': 'assistant'
                    },
                    'finish_reason': 'stop'
                }],
                'usage': {
                    'prompt_tokens': 150,
                    'completion_tokens': 50,
                    'total_tokens': 200
                },
                'model': kwargs.get('model', 'gpt-4'),
                'created': 1234567890
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