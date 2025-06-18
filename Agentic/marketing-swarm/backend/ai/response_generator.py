"""
AI Response Generator for Marketing Swarm
Generates dynamic, personality-driven responses using GPT-4
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger

from utils.openai_helper import get_openai_client
from ai.prompts import (
    build_agent_system_prompt,
    build_reaction_prompt,
    build_interruption_prompt,
    format_conversation_context
)


class AIResponseGenerator:
    """Handles AI-powered response generation for agents"""
    
    def __init__(self):
        self.client = get_openai_client()
        self.model = os.getenv("AI_MODEL", "gpt-4")
        self.default_temperature = float(os.getenv("AI_DEFAULT_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("AI_MAX_TOKENS", "300"))
        self.enable_streaming = os.getenv("AI_ENABLE_STREAMING", "true").lower() == "true"
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_response(
        self,
        agent_id: str,
        agent_data: Dict,
        query: str,
        conversation_history: List[Dict],
        is_reaction: bool = False,
        is_interruption: bool = False,
        target_agent: Optional[str] = None
    ) -> str:
        """
        Generate AI-powered response maintaining agent personality
        
        Args:
            agent_id: Unique identifier for the agent
            agent_data: Agent configuration including personality traits
            query: User's original query
            conversation_history: List of previous responses
            is_reaction: Whether this is a reaction to another agent
            is_interruption: Whether this is an interruption
            target_agent: Agent being reacted to or interrupted
            
        Returns:
            Generated response string
        """
        try:
            # Build appropriate system prompt based on context
            if is_interruption and target_agent:
                system_prompt = build_interruption_prompt(agent_data, target_agent)
            elif is_reaction and conversation_history:
                system_prompt = build_reaction_prompt(
                    agent_data, 
                    conversation_history[-1] if conversation_history else None
                )
            else:
                system_prompt = build_agent_system_prompt(agent_data)
            
            # Format conversation context
            context = format_conversation_context(
                conversation_history, 
                max_exchanges=10,  # Limit context to prevent token overflow
                agent_id=agent_id
            )
            
            # Adjust temperature based on agent personality
            temperature = self._calculate_temperature(agent_data, is_reaction)
            
            # Build messages for OpenAI
            messages = self._build_messages(
                system_prompt, 
                query, 
                context,
                agent_data,
                is_reaction,
                is_interruption
            )
            
            # Generate response
            if self.enable_streaming:
                return await self._generate_streaming_response(messages, temperature)
            else:
                return await self._generate_standard_response(messages, temperature)
                
        except Exception as e:
            logger.error(f"Error generating AI response for {agent_id}: {e}")
            # Fallback to a personality-appropriate error response
            return self._get_fallback_response(agent_data, query)
    
    def _calculate_temperature(self, agent_data: Dict, is_reaction: bool) -> float:
        """Calculate temperature based on agent personality"""
        base_temp = self.default_temperature
        
        # Adjust based on creativity trait
        creativity = agent_data.get('creativity', 0.5)
        temp_adjustment = (creativity - 0.5) * 0.4  # -0.2 to +0.2 adjustment
        
        # Reactions tend to be more varied
        if is_reaction:
            temp_adjustment += 0.1
            
        # High contrarianism = more varied responses
        contrarianism = agent_data.get('contrarianism', 0.5)
        if contrarianism > 0.7:
            temp_adjustment += 0.1
            
        final_temp = max(0.3, min(1.0, base_temp + temp_adjustment))
        return final_temp
    
    def _build_messages(
        self, 
        system_prompt: str, 
        query: str, 
        context: str,
        agent_data: Dict,
        is_reaction: bool,
        is_interruption: bool
    ) -> List[Dict[str, str]]:
        """Build message array for OpenAI API"""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation context if available
        if context:
            messages.append({
                "role": "assistant", 
                "content": f"Previous conversation context:\n{context}"
            })
        
        # Build user message based on type
        if is_interruption:
            user_content = (
                f"The current speaker is saying something you strongly disagree with. "
                f"Interrupt them mid-sentence about: {query}\n\n"
                f"Start your response with [interrupting] or [talking over] to indicate the interruption."
            )
        elif is_reaction:
            user_content = (
                f"React to what was just said, considering: {query}\n\n"
                f"Your response should directly address the previous speaker's points."
            )
        else:
            user_content = (
                f"Analyze and respond to this marketing challenge: {query}\n\n"
                f"Provide specific, actionable insights from your {agent_data['role']} perspective."
            )
            
        messages.append({"role": "user", "content": user_content})
        
        return messages
    
    async def _generate_standard_response(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float
    ) -> str:
        """Generate non-streaming response"""
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=self.max_tokens,
            presence_penalty=0.1,  # Encourage variety
            frequency_penalty=0.1   # Reduce repetition
        )
        
        return response.choices[0].message.content
    
    async def _generate_streaming_response(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float
    ) -> str:
        """Generate streaming response (simplified for now)"""
        # For initial launch, use standard response
        # Streaming can be added later once core functionality is stable
        return await self._generate_standard_response(messages, temperature)
    
    def _get_fallback_response(self, agent_data: Dict, query: str) -> str:
        """Generate fallback response when AI fails"""
        role = agent_data.get('role', 'Marketing Specialist')
        name = agent_data.get('name', 'Agent')
        
        fallback_responses = {
            'Brand Strategy Lead': f"As {name}, I believe we need to focus on brand differentiation in addressing {query[:50]}...",
            'Digital Campaign Manager': f"From a campaign perspective, {query[:50]}... requires data-driven optimization.",
            'Content Marketing Specialist': f"The content angle for {query[:50]}... should focus on authentic storytelling.",
            'Customer Experience Designer': f"User experience considerations for {query[:50]}... are critical to success.",
            'Marketing Analytics Manager': f"The data implications of {query[:50]}... need careful analysis.",
            'Growth Marketing Lead': f"For rapid growth with {query[:50]}..., we need to experiment aggressively."
        }
        
        return fallback_responses.get(
            role, 
            f"Let me analyze {query[:50]}... from my {role} perspective."
        )
    
    async def generate_briefing_contribution(
        self,
        agent_data: Dict,
        section: str,
        context: Dict
    ) -> str:
        """Generate agent's contribution to briefing document"""
        system_prompt = f"""You are {agent_data['name']}, a {agent_data['role']} with expertise in {agent_data['expertise']}.
        
You are contributing to the {section} section of a strategic briefing document.
Your contribution should be:
- Specific and actionable
- Based on your domain expertise
- Professional consultant-level quality
- 2-3 sentences maximum
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Provide your {section} contribution based on the team discussion: {json.dumps(context, indent=2)}"}
        ]
        
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model,
            messages=messages,
            temperature=0.5,  # Lower temperature for more focused briefing content
            max_tokens=150
        )
        
        return response.choices[0].message.content


# Global instance
ai_generator = AIResponseGenerator()