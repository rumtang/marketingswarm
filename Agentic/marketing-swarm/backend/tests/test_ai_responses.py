"""
Tests for AI Response Generation
"""

import asyncio
import os
import pytest
from unittest.mock import Mock, patch, AsyncMock

# Set up test environment
os.environ["MOCK_API_RESPONSES"] = "true"
os.environ["USE_AI_RESPONSES"] = "true"

from ai.response_generator import AIResponseGenerator
from ai.prompts import build_agent_system_prompt
from ai.context_manager import ContextManager


class TestAIResponseGenerator:
    """Test AI response generation"""
    
    @pytest.fixture
    def ai_generator(self):
        """Create AI generator instance"""
        return AIResponseGenerator()
    
    @pytest.fixture
    def sample_agent_data(self):
        """Sample agent data for testing"""
        return {
            'name': 'Sarah',
            'role': 'Brand Strategy Lead',
            'expertise': 'Brand positioning, competitive analysis',
            'personality': 'Visionary idealist',
            'assertiveness': 0.8,
            'contrarianism': 0.4,
            'creativity': 0.7,
            'patience': 0.6
        }
    
    @pytest.fixture
    def sample_conversation_history(self):
        """Sample conversation history"""
        return [
            {
                'agent': 'marcus',
                'message': 'We need to focus on data-driven metrics for ROI.',
                'timestamp': '2024-01-01T12:00:00'
            },
            {
                'agent': 'elena',
                'message': 'But creative storytelling drives emotional connection!',
                'timestamp': '2024-01-01T12:01:00'
            }
        ]
    
    @pytest.mark.asyncio
    async def test_generate_standard_response(self, ai_generator, sample_agent_data):
        """Test standard response generation"""
        response = await ai_generator.generate_response(
            agent_id='sarah',
            agent_data=sample_agent_data,
            query='How should we launch our new robo-advisor?',
            conversation_history=[]
        )
        
        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)
    
    @pytest.mark.asyncio
    async def test_generate_reaction_response(self, ai_generator, sample_agent_data, sample_conversation_history):
        """Test reaction response generation"""
        response = await ai_generator.generate_response(
            agent_id='sarah',
            agent_data=sample_agent_data,
            query='How should we launch our new robo-advisor?',
            conversation_history=sample_conversation_history,
            is_reaction=True
        )
        
        assert response is not None
        # Mock response should be appropriate
        assert 'mock response' in response.lower() or len(response) > 0
    
    @pytest.mark.asyncio
    async def test_generate_interruption_response(self, ai_generator, sample_agent_data, sample_conversation_history):
        """Test interruption response generation"""
        response = await ai_generator.generate_response(
            agent_id='sarah',
            agent_data=sample_agent_data,
            query='How should we launch our new robo-advisor?',
            conversation_history=sample_conversation_history,
            is_interruption=True,
            target_agent='marcus'
        )
        
        assert response is not None
        assert len(response) > 0
    
    def test_calculate_temperature(self, ai_generator, sample_agent_data):
        """Test temperature calculation based on personality"""
        # High creativity should increase temperature
        high_creativity_agent = sample_agent_data.copy()
        high_creativity_agent['creativity'] = 0.9
        temp = ai_generator._calculate_temperature(high_creativity_agent, False)
        assert temp > 0.7  # Should be higher than default
        
        # Low creativity should decrease temperature
        low_creativity_agent = sample_agent_data.copy()
        low_creativity_agent['creativity'] = 0.2
        temp = ai_generator._calculate_temperature(low_creativity_agent, False)
        assert temp < 0.7  # Should be lower than default
        
        # Reactions should have slightly higher temperature
        temp_reaction = ai_generator._calculate_temperature(sample_agent_data, True)
        temp_normal = ai_generator._calculate_temperature(sample_agent_data, False)
        assert temp_reaction > temp_normal
    
    def test_build_messages(self, ai_generator, sample_agent_data):
        """Test message building for OpenAI API"""
        messages = ai_generator._build_messages(
            system_prompt="Test system prompt",
            query="Test query",
            context="Test context",
            agent_data=sample_agent_data,
            is_reaction=False,
            is_interruption=False
        )
        
        assert len(messages) == 3  # System, context, user
        assert messages[0]['role'] == 'system'
        assert messages[1]['role'] == 'assistant'
        assert messages[2]['role'] == 'user'
        assert 'Test query' in messages[2]['content']
    
    def test_fallback_response(self, ai_generator, sample_agent_data):
        """Test fallback response generation"""
        response = ai_generator._get_fallback_response(
            sample_agent_data,
            "How to improve customer acquisition?"
        )
        
        assert response is not None
        assert 'Sarah' in response
        assert 'brand' in response.lower()


class TestPrompts:
    """Test prompt generation"""
    
    def test_build_agent_system_prompt(self):
        """Test system prompt generation"""
        agent_data = {
            'name': 'Marcus',
            'role': 'Digital Campaign Manager',
            'expertise': 'Paid advertising, campaign optimization',
            'personality': 'Data evangelist',
            'assertiveness': 0.9,
            'contrarianism': 0.8,
            'creativity': 0.3,
            'patience': 0.2
        }
        
        prompt = build_agent_system_prompt(agent_data)
        
        assert 'Marcus' in prompt
        assert 'Digital Campaign Manager' in prompt
        assert 'Data evangelist' in prompt
        assert 'assertiveness' in prompt.lower()
        assert 'ROI' in prompt  # Should include domain-specific terms
    
    def test_personality_descriptions(self):
        """Test personality trait descriptions"""
        from ai.prompts import _get_assertiveness_description
        
        # Test different assertiveness levels
        assert 'reserved' in _get_assertiveness_description(0.2)
        assert 'confident' in _get_assertiveness_description(0.7)
        assert 'dominate' in _get_assertiveness_description(0.95)


class TestContextManager:
    """Test context management"""
    
    @pytest.fixture
    def context_manager(self):
        """Create context manager instance"""
        return ContextManager()
    
    def test_build_context(self, context_manager):
        """Test context building"""
        conversation_history = [
            {
                'agent': 'sarah',
                'message': 'We should focus on brand positioning.',
                'timestamp': '2024-01-01T12:00:00'
            },
            {
                'agent': 'marcus',
                'message': 'I disagree, we need data-driven metrics.',
                'timestamp': '2024-01-01T12:01:00'
            }
        ]
        
        context = context_manager.build_context(
            agent_id='elena',
            agent_data={'name': 'Elena', 'role': 'Content Marketing'},
            query='How to create engaging content?',
            conversation_history=conversation_history
        )
        
        assert 'User Query:' in context
        assert 'brand positioning' in context
        assert 'disagree' in context
    
    def test_relevance_scoring(self, context_manager):
        """Test relevance scoring for context items"""
        item = {
            'agent': 'marcus',
            'message': 'Elena, I disagree with your creative approach. We need 25% ROI.',
            'timestamp': '2024-01-01T12:00:00'
        }
        
        score = context_manager._calculate_relevance_score(
            agent_id='elena',
            agent_data={'name': 'Elena'},
            item=item,
            position=0,
            total_items=10
        )
        
        # Should have high score due to direct mention and disagreement
        assert score > 1.0
    
    def test_extract_key_insights(self, context_manager):
        """Test insight extraction from conversation"""
        conversation_history = [
            {
                'agent': 'sarah',
                'message': 'I recommend focusing on brand trust with a $50K budget.',
                'timestamp': '2024-01-01T12:00:00'
            },
            {
                'agent': 'marcus',
                'message': 'I disagree. Data shows 35% better ROI with performance marketing.',
                'timestamp': '2024-01-01T12:01:00'
            }
        ]
        
        insights = context_manager.extract_key_insights(conversation_history)
        
        assert len(insights['recommendations']) > 0
        assert len(insights['data_points']) > 0
        assert len(insights['disagreements']) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])