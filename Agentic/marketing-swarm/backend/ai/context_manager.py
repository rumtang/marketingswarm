"""
Context Manager for AI Response Generation
Manages conversation context to optimize token usage and relevance
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
from collections import defaultdict


class ContextManager:
    """Manages conversation context for AI responses"""
    
    def __init__(self, max_context_length: int = 3000):
        self.max_context_length = max_context_length
        self.importance_weights = {
            'user_query': 1.0,
            'direct_mention': 0.9,
            'recent': 0.8,
            'disagreement': 0.7,
            'agreement': 0.6,
            'data_point': 0.7,
            'recommendation': 0.8,
            'same_domain': 0.5
        }
        
    def build_context(
        self,
        agent_id: str,
        agent_data: Dict,
        query: str,
        conversation_history: List[Dict],
        include_relationships: bool = True
    ) -> str:
        """Build optimized context for AI response generation"""
        
        # Start with the user query
        context_parts = [f"User Query: {query}"]
        
        # Add relevant conversation history
        if conversation_history:
            relevant_history = self._select_relevant_history(
                agent_id, 
                conversation_history,
                agent_data
            )
            
            if relevant_history:
                context_parts.append("\nRelevant Conversation History:")
                for item in relevant_history:
                    context_parts.append(self._format_history_item(item))
        
        # Add relationship context if enabled
        if include_relationships and conversation_history:
            relationship_summary = self._summarize_relationships(
                agent_id,
                conversation_history
            )
            if relationship_summary:
                context_parts.append(f"\nTeam Dynamics: {relationship_summary}")
        
        # Combine and truncate if necessary
        full_context = "\n".join(context_parts)
        if len(full_context) > self.max_context_length:
            return self._truncate_context(full_context)
            
        return full_context
    
    def _select_relevant_history(
        self, 
        agent_id: str,
        conversation_history: List[Dict],
        agent_data: Dict
    ) -> List[Dict]:
        """Select most relevant parts of conversation history"""
        
        scored_items = []
        
        for i, item in enumerate(conversation_history):
            score = self._calculate_relevance_score(
                agent_id,
                agent_data,
                item,
                i,
                len(conversation_history)
            )
            
            scored_items.append((score, item))
        
        # Sort by relevance score and take top items
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        # Take items until we approach token limit
        selected_items = []
        current_length = 0
        
        for score, item in scored_items:
            item_length = len(str(item.get('message', '')))
            if current_length + item_length > self.max_context_length * 0.7:
                break
            selected_items.append(item)
            current_length += item_length
            
        # Sort selected items by timestamp to maintain flow
        selected_items.sort(key=lambda x: x.get('timestamp', ''))
        
        return selected_items
    
    def _calculate_relevance_score(
        self,
        agent_id: str,
        agent_data: Dict,
        item: Dict,
        position: int,
        total_items: int
    ) -> float:
        """Calculate relevance score for a conversation item"""
        
        score = 0.0
        message = item.get('message', '').lower()
        item_agent = item.get('agent', '')
        
        # Recency bonus
        recency_factor = (position + 1) / total_items
        score += self.importance_weights['recent'] * recency_factor
        
        # Direct mention bonus
        if agent_id in message or agent_data['name'].lower() in message:
            score += self.importance_weights['direct_mention']
            
        # Disagreement/agreement detection
        if any(word in message for word in ['disagree', 'wrong', 'but', 'however']):
            score += self.importance_weights['disagreement']
        elif any(word in message for word in ['agree', 'exactly', 'right', 'yes']):
            score += self.importance_weights['agreement']
            
        # Data points and recommendations
        if any(char in message for char in ['$', '%']) or any(word in message for word in ['data', 'metrics']):
            score += self.importance_weights['data_point']
        if any(word in message for word in ['recommend', 'suggest', 'should']):
            score += self.importance_weights['recommendation']
            
        # Same domain expertise bonus
        if self._is_same_domain(agent_data, item_agent):
            score += self.importance_weights['same_domain']
            
        return score
    
    def _is_same_domain(self, agent_data: Dict, other_agent: str) -> bool:
        """Check if agents share domain expertise"""
        
        domain_groups = {
            'data': ['marcus', 'priya'],
            'creative': ['elena', 'david'],
            'strategy': ['sarah', 'alex']
        }
        
        agent_name = agent_data.get('name', '').lower()
        
        for group, members in domain_groups.items():
            if agent_name in members and other_agent.lower() in members:
                return True
                
        return False
    
    def _format_history_item(self, item: Dict) -> str:
        """Format a history item for context"""
        agent = item.get('agent', 'Unknown')
        message = item.get('message', '')
        
        # Truncate long messages
        if len(message) > 300:
            message = message[:297] + "..."
            
        return f"{agent.title()}: {message}"
    
    def _summarize_relationships(
        self,
        agent_id: str,
        conversation_history: List[Dict]
    ) -> str:
        """Summarize team dynamics and relationships"""
        
        relationships = defaultdict(int)
        
        for i, item in enumerate(conversation_history):
            if i == 0:
                continue
                
            current_agent = item.get('agent', '')
            previous_agent = conversation_history[i-1].get('agent', '')
            message = item.get('message', '').lower()
            
            # Track interactions
            if current_agent == agent_id:
                if any(word in message for word in ['agree', 'exactly', 'right']):
                    relationships[f"agrees_with_{previous_agent}"] += 1
                elif any(word in message for word in ['disagree', 'wrong', 'but']):
                    relationships[f"disagrees_with_{previous_agent}"] += 1
                    
        # Build summary
        summary_parts = []
        for rel, count in relationships.items():
            if count > 1:
                summary_parts.append(f"{rel.replace('_', ' ')}: {count} times")
                
        return ", ".join(summary_parts) if summary_parts else ""
    
    def _truncate_context(self, context: str) -> str:
        """Intelligently truncate context to fit token limits"""
        
        # Try to truncate at sentence boundaries
        sentences = context.split('. ')
        truncated = []
        current_length = 0
        
        for sentence in sentences:
            if current_length + len(sentence) > self.max_context_length:
                break
            truncated.append(sentence)
            current_length += len(sentence)
            
        return '. '.join(truncated) + '...'
    
    def extract_key_insights(self, conversation_history: List[Dict]) -> Dict[str, List[str]]:
        """Extract key insights from conversation for briefing"""
        
        insights = {
            'recommendations': [],
            'data_points': [],
            'disagreements': [],
            'consensus_points': []
        }
        
        for item in conversation_history:
            message = item.get('message', '')
            agent = item.get('agent', '')
            
            # Extract recommendations
            if any(word in message.lower() for word in ['recommend', 'suggest', 'should']):
                insights['recommendations'].append({
                    'agent': agent,
                    'content': message[:200]
                })
                
            # Extract data points
            if '$' in message or '%' in message:
                # Simple extraction of sentences with data
                sentences = message.split('. ')
                for sentence in sentences:
                    if '$' in sentence or '%' in sentence:
                        insights['data_points'].append({
                            'agent': agent,
                            'content': sentence
                        })
                        
            # Track disagreements
            if any(word in message.lower() for word in ['disagree', 'wrong', 'challenge']):
                insights['disagreements'].append({
                    'agent': agent,
                    'content': message[:150]
                })
                
            # Track consensus
            if any(word in message.lower() for word in ['agree', 'exactly', 'consensus']):
                insights['consensus_points'].append({
                    'agent': agent,
                    'content': message[:150]
                })
                
        return insights


# Global instance
context_manager = ContextManager()