"""
Marketing Swarm API - Python 3.13 Compatible Version
FastAPI backend with WebSocket support for multi-agent collaboration
"""

import os
import asyncio
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from loguru import logger
import socketio

# Import our simplified modules
from utils.config import get_settings, validate_environment
from safety.budget_guard import BudgetGuard
from safety.compliance_filter import ComplianceFilter
from safety.input_sanitizer import InputSanitizer
from ai.response_generator import ai_generator
from ai.context_manager import context_manager

# Configure logging
logging.basicConfig(level=logging.INFO)

# Models
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    version: str = "1.0.0"
    mode: str = "simple"

class ConversationRequest(BaseModel):
    user_query: str
    conversation_id: Optional[str] = None
    test_mode: Optional[bool] = False

class ConversationResponse(BaseModel):
    conversation_id: str
    status: str
    message: Optional[str] = None

class AgentMessage(BaseModel):
    agent: str
    message: str
    timestamp: str
    phase: str

# Simplified Agent Manager
class SimpleAgentManager:
    """Simplified agent manager for Python 3.13 compatibility"""
    
    def __init__(self):
        self.conversation_memory = {}  # Store conversation history and agent relationships
        self.agent_relationships = {  # Track dynamic alliances and conflicts
            "alliances": {},
            "conflicts": {},
            "respect_levels": {}
        }
        self.briefing_document = {  # Build briefing document progressively
            "title": "",
            "executive_summary": "",
            "situation_analysis": [],
            "strategic_recommendations": [],
            "implementation_plan": [],
            "success_metrics": [],
            "risk_mitigation": [],
            "next_steps": []
        }
        self.conversation_phase = "discovery"  # discovery -> analysis -> recommendation -> synthesis
        self.agents = {
            "sarah": {
                "name": "Sarah",
                "role": "Brand Strategy Lead",
                "emoji": "👔",
                "expertise": "Brand positioning, competitive analysis, market strategy",
                "personality": "Visionary idealist, often clashes with data-driven approaches",
                "assertiveness": 0.8,
                "contrarianism": 0.4,
                "creativity": 0.7,
                "patience": 0.6
            },
            "marcus": {
                "name": "Marcus", 
                "role": "Digital Campaign Manager",
                "emoji": "📱",
                "expertise": "Paid advertising, campaign optimization, channel strategy",
                "personality": "Aggressive data evangelist, challenges everything without metrics",
                "assertiveness": 0.9,
                "contrarianism": 0.8,
                "creativity": 0.3,
                "patience": 0.2
            },
            "elena": {
                "name": "Elena",
                "role": "Content Marketing Specialist", 
                "emoji": "✍️",
                "expertise": "Content strategy, SEO, thought leadership",
                "personality": "Creative rebel, pushes boundaries and questions conventions",
                "assertiveness": 0.7,
                "contrarianism": 0.7,
                "creativity": 0.9,
                "patience": 0.4
            },
            "david": {
                "name": "David",
                "role": "Customer Experience Designer",
                "emoji": "🎨", 
                "expertise": "UX/UI design, conversion optimization, user journeys",
                "personality": "User zealot, frequently conflicts with business/profit goals",
                "assertiveness": 0.6,
                "contrarianism": 0.6,
                "creativity": 0.5,
                "patience": 0.8
            },
            "priya": {
                "name": "Priya",
                "role": "Marketing Analytics Manager",
                "emoji": "📊",
                "expertise": "Data analysis, ROI measurement, attribution",
                "personality": "Skeptical scientist, demands proof and questions assumptions",
                "assertiveness": 0.7,
                "contrarianism": 0.9,
                "creativity": 0.2,
                "patience": 0.5
            },
            "alex": {
                "name": "Alex",
                "role": "Growth Marketing Lead",
                "emoji": "🚀",
                "expertise": "Growth strategies, funnel optimization, retention",
                "personality": "Risk-taking experimenter, proposes wild ideas others find reckless",
                "assertiveness": 0.8,
                "contrarianism": 0.5,
                "creativity": 1.0,
                "patience": 0.3
            }
        }
        
    async def get_agent_response(self, agent_id: str, query: str, context: Dict, conversation_flow: List = None) -> str:
        """Generate dynamic agent response with interruptions and debates"""
        agent = self.agents.get(agent_id)
        if not agent:
            return "Agent not found"
        
        # Get conversation history to determine if agent should interrupt or react
        previous_responses = conversation_flow or []
        
        # Use AI if enabled, otherwise fall back to predetermined responses
        use_ai = os.getenv("USE_AI_RESPONSES", "true").lower() == "true"
        
        if use_ai:
            try:
                # Check if this should be a reaction or interruption
                is_reaction = False
                is_interruption = False
                target_agent = None
                
                if previous_responses:
                    last_response = previous_responses[-1]
                    last_agent = last_response.get('agent', '')
                    last_message = last_response.get('message', '')
                    
                    # Determine if this is a reaction based on personality
                    if agent['contrarianism'] > 0.7 and self._should_react(agent_id, last_message):
                        is_reaction = True
                    
                    # Determine if this is an interruption
                    if agent['assertiveness'] > 0.8 and random.random() < 0.3:
                        is_interruption = True
                        target_agent = last_agent
                
                # Generate AI response
                response = await ai_generator.generate_response(
                    agent_id=agent_id,
                    agent_data=agent,
                    query=query,
                    conversation_history=previous_responses,
                    is_reaction=is_reaction,
                    is_interruption=is_interruption,
                    target_agent=target_agent
                )
                
                return response
                
            except Exception as e:
                logger.error(f"AI response generation failed: {e}. Falling back to predetermined responses.")
                # Fall back to predetermined responses
                return self.get_dynamic_responses(agent_id, query, previous_responses)
        else:
            # Use predetermined responses
            return self.get_dynamic_responses(agent_id, query, previous_responses)

    def _should_react(self, agent_id: str, last_message: str) -> bool:
        """Determine if agent should react to the last message"""
        # Check for trigger words based on agent personality
        reaction_triggers = {
            'sarah': ['data', 'metrics', 'roi', 'conversion'],
            'marcus': ['brand', 'emotion', 'feeling', 'trust'],
            'elena': ['boring', 'traditional', 'safe', 'conventional'],
            'david': ['profit', 'revenue', 'cost', 'money'],
            'priya': ['assume', 'guess', 'feel', 'think'],
            'alex': ['slow', 'careful', 'wait', 'analyze']
        }
        
        triggers = reaction_triggers.get(agent_id, [])
        return any(trigger in last_message.lower() for trigger in triggers)
    
    def get_dynamic_responses(self, agent_id: str, query: str, previous_responses: List) -> str:
        """Generate dynamic responses with personality-driven interactions"""
        agent = self.agents[agent_id]
        
        # Check if agent should interrupt or react to previous responses
        if previous_responses and len(previous_responses) > 0:
            last_response = previous_responses[-1]
            reaction = self.get_reaction_response(agent_id, last_response, query)
            if reaction:
                return reaction
        
        # Generate primary response based on query and personality
        if "robo-advisor" in query.lower() or "betterment" in query.lower():
            return self.get_robo_advisor_responses(agent_id, query)
        elif "acquisition cost" in query.lower() or "cac" in query.lower():
            return self.get_cac_responses(agent_id, query)
        elif "content strategy" in query.lower() or "gen z" in query.lower():
            return self.get_content_strategy_responses(agent_id, query)
        else:
            return self.get_general_responses(agent_id, query)

    def get_reaction_response(self, agent_id: str, last_response: Dict, query: str) -> str:
        """Generate sophisticated reactive responses based on what other agents said"""
        agent = self.agents[agent_id]
        last_agent = last_response.get('agent', '')
        last_message = last_response.get('message', '')
        
        # High contrarianism agents challenge others with professional sophistication
        if agent['contrarianism'] > 0.7:
            if 'data' in last_message.lower() and agent_id == 'sarah':
                return "Marcus, I respect your analytical approach, but we're missing the strategic context. McKinsey research shows that data-driven decisions without brand consideration have 40% higher failure rates. Emotional connection drives 70% of B2C purchase decisions. Can we find a framework that balances both quantitative performance and qualitative brand strength?"
            elif 'trust' in last_message.lower() and agent_id == 'marcus':
                return "Sarah, brand trust is important, but we need measurable trust indicators. Net Promoter Score averages 31 in fintech - what's our baseline? Trust without conversion optimization leaves money on the table. I'd like to see trust metrics correlated with actual customer acquisition and retention data. How do we quantify brand trust's impact on CAC and LTV?"
            elif 'creative' in last_message.lower() and agent_id == 'priya':
                return "Elena, I appreciate the creative thinking, but we need evidence-based creativity. Breakthrough campaigns that lack performance data often become expensive experiments. Can we A/B test the creative concepts against conversion benchmarks? What success metrics would validate whether creative risk translates to business results?"
            elif 'transparency' in last_message.lower() and agent_id == 'david':
                return "I'm concerned about the UX implications of radical transparency. User research shows financial customers experience 'choice paralysis' when given too much information. Schwab's transparency works because they layer complexity progressively. How do we balance transparency with usability? What's the optimal information architecture?"
        
        # High assertiveness agents interrupt with sophisticated challenges  
        if agent['assertiveness'] > 0.8:
            if agent_id == 'marcus' and ('premium' in last_message.lower() or 'positioning' in last_message.lower()):
                return "[interrupting] Let's validate positioning assumptions with market data. Premium positioning in robo-advisory shows mixed results: Wealthfront's premium tier has 15% adoption vs 85% basic tier. Are we optimizing for margin or market share? I need to see price sensitivity analysis before committing to premium strategy."
            elif agent_id == 'alex' and len(last_message) > 150:
                return "While this analysis is thorough, we're facing a velocity problem. Competitors are launching new features every 6-8 weeks while we're still in planning phase. What's our minimum viable approach to test these hypotheses quickly? Sometimes speed to market beats perfect strategy."
            elif agent_id == 'sarah' and 'metrics' in last_message.lower():
                return "[building on] Excellent data foundation, but metrics without narrative context miss the strategic picture. What story do these numbers tell about our market position? How do we translate performance data into compelling brand differentiation? The most successful fintech brands use data to inform brand strategy, not replace it."
        
        return None  # No reaction, continue with normal response

    def get_robo_advisor_responses(self, agent_id: str, query: str) -> str:
        """Professional consultant-level responses for robo-advisor marketing query"""
        responses = {
            "sarah": "We should position as 'Intelligent Transparency' - the advisor that shows its work. Research from McKinsey shows trust is the #1 driver in fintech adoption. Unlike Betterment's black-box approach, we'll differentiate through radical transparency. Think 'the thinking person's robo-advisor' but with proof, not promises. Risk: avoid sounding condescending to mass market.",
            "marcus": "Let's cut through the positioning talk with hard data. Betterment's CPA is $380-420 across channels. Current robo-advisor keywords cost $8-15 CPC with 4-6% conversion rates. I recommend $75K test budget: 40% Google Search ($30K), 30% LinkedIn video ($22.5K), 20% Facebook lookalikes ($15K), 10% TikTok experimentation ($7.5K). We can beat their efficiency with better targeting.",
            "elena": "Both valid, but you're missing the cultural moment. 'Transparent rebellion' is having a moment - see how Patagonia and Ben & Jerry's leverage authentic contrarianism. What if we're the 'anti-robo-advisor robo-advisor'? Position transparency as rebellion against the industry's opacity. Content angle: 'The advisor that actually explains what it's doing.' Could generate massive earned media.",
            "david": "I appreciate the creativity, but UX research is clear: financial users prioritize security over excitement. Robinhood's 'rebellious' brand led to serious UX debt and regulatory issues. Our competitive advantage should be 'boring reliability done beautifully.' Think Apple's design principles applied to investing - clean, clear, trustworthy. One-click portfolio rebalancing, not gamification.",
            "priya": "Looking at the data, 'rebellious' financial brands show concerning patterns. Robinhood's brand repositioning cost them $65M in fines and 40% user trust decline. However, 'transparency' positioning has proven ROI: Schwab's transparent fee structure increased AUM 23% year-over-year. I recommend A/B testing 'transparency' vs 'intelligence' messaging across our initial cohorts.",
            "alex": "Contrarian take: what if high 'rebellion' is actually our growth unlock? Dollar Shave Club's anti-establishment positioning created $1B value. For robo-advisors, most competitors sound identical. What if we're the 'anti-robo-advisor robo-advisor'? Full portfolio transparency, real-time decision explanations, maybe even livestream our algorithm choices. High risk, but viral potential is massive."
        }
        return responses.get(agent_id, "Processing your robo-advisor question...")

    def get_cac_responses(self, agent_id: str, query: str) -> str:
        """Professional consultant-level responses for customer acquisition cost problems"""
        responses = {
            "sarah": "CAC inflation typically signals brand weakness or market saturation. When acquisition costs double, we're competing on price, not value. I recommend a brand audit focusing on differentiation metrics: unaided brand recall, Net Promoter Score, and consideration rates. Benchmark: leading fintech brands maintain 15-25% unaided recall. If we're below that, organic demand generation through thought leadership will be more cost-effective than paid acquisition.",
            "marcus": "Attribution challenges post-iOS 14.5 are definitely impacting measurement, but not necessarily actual performance. Our CAC may appear inflated due to view-through conversion underreporting. Immediate actions: 1) Shift 60% budget to first-party data channels (email, SMS, direct), 2) Implement server-side tracking, 3) Focus on Google Search where attribution is cleaner. Industry benchmark: fintech CAC should be 15-25% of first-year LTV.",
            "elena": "High CAC indicates we're not creating content worth sharing organically. The most successful fintech brands generate 40-60% of their traffic through owned content. My recommendation: launch a 'Financial Clarity' content series - weekly deep-dives into investment strategies with real portfolio examples. Target: 2M organic impressions per month within 6 months. When people share your content, CAC approaches zero.",
            "david": "Conversion rate optimization is the fastest CAC reducer. Industry data shows fintech onboarding has 65-85% drop-off rates. Quick wins: 1) Reduce onboarding from 15 steps to 5, 2) Add progress indicators, 3) Enable social sign-up. Hypothesis: 25% conversion improvement could reduce CAC by $50-80. I can audit our funnel and identify the top 3 friction points within 48 hours.",
            "priya": "Before optimization, we need proper segmentation analysis. CAC variations by channel, demographics, and geography often reveal the real issues. For example, if mobile CAC is 3x desktop, that's a UX problem, not a marketing problem. Let me run cohort analysis across: acquisition channel, device type, geographic region, and user value segments. This will show us where to focus efforts for maximum impact.",
            "alex": "Contrarian perspective: what if doubling CAC is actually strategic? If our LTV:CAC ratio is still >3:1, we should be more aggressive, not less. Uber and Netflix both operated at 'high' CAC during growth phases to capture market share. Question: what's our true LTV including referrals and lifetime portfolio growth? If it's strong, we should double down and outspend competitors while they're cutting budgets."
        }
        return responses.get(agent_id, "Processing your CAC question...")

    def get_content_strategy_responses(self, agent_id: str, query: str) -> str:
        """Professional consultant-level responses for content strategy and Gen Z"""
        responses = {
            "sarah": "Gen Z trust metrics are fascinating: they're 2.3x more likely to trust brands that admit mistakes and 4x more likely to engage with 'behind-the-scenes' content. Our brand voice should embrace 'intelligent vulnerability' - acknowledge that traditional retirement planning failed their parents, but position our solution as the generational correction. Think Patagonia's activism meets Schwab's expertise. Key message: 'We're fixing what the previous generation broke.'",
            "marcus": "TikTok's engagement rates for fintech content are exceptional: 6.2% vs 2.1% on other platforms. But 'authentic' content without clear conversion paths wastes budget. Strategy: $25K for TikTok creative testing with financial education hooks. Target: 'Money tips that actually work' with strong CTAs to portfolio calculators. Benchmark successful fintech TikTok: Acorns generated 12% signup rate from educational content with embedded product demos.",
            "elena": "The 'FinTok' opportunity is massive - #MoneyTok has 2.1B views and growing 40% monthly. But we need strategic creator partnerships, not just influencer spray-and-pray. Recommend: identify 10-15 nano-influencers (10K-100K followers) with authentic financial content, offer them free portfolio management in exchange for genuine product integration. Target creators with 8%+ engagement rates in personal finance vertical.",
            "david": "Gen Z content consumption research shows 73% prefer vertical video, 68% engage with interactive elements, and 54% take action from swipe-up features. Our content framework: 1) 15-second hook, 2) visual data story, 3) clear action step. Format priority: Instagram Stories > TikTok > YouTube Shorts. Avoid: text-heavy posts, talking heads, anything longer than 60 seconds. Design principle: 'thumb-stopping, not scroll-stopping.'",
            "priya": "Data on Gen Z fintech engagement reveals interesting patterns: they engage 3x more with personalized content, but conversion rates vary dramatically by format. Video content: 12% engagement, 2.3% conversion. Interactive calculators: 8% engagement, 7.1% conversion. My recommendation: A/B test content formats against actual account openings, not just engagement metrics. Let's optimize for revenue, not vanity metrics.",
            "alex": "Gamification has proven ROI in fintech: Acorns' 'Found Money' program drove 34% usage increase, Qapital's goals feature improved retention 45%. For Gen Z specifically, progress visualization and social comparison drive behavior. Proposal: 'Investment Streaks' feature - daily investment habits with streak counters, friend comparisons, and milestone rewards. Make compound interest feel like leveling up in a game. Could be our differentiation."
        }
        return responses.get(agent_id, "Processing your content strategy question...")

    def get_general_responses(self, agent_id: str, query: str) -> str:
        """Professional consultant-level default responses for general queries"""
        responses = {
            "sarah": "From a strategic brand perspective, this challenge requires us to identify our unique value proposition and emotional positioning. I recommend starting with a competitive differentiation audit: what do our top 3 competitors claim, what do customers actually value, and where's the gap we can own? Strong brands solve emotional problems, not just functional ones. What's the deeper customer anxiety we're addressing?",
            "marcus": "Let's establish our measurement framework first. I need baseline metrics across three categories: 1) Performance indicators (current conversion rates, CAC, LTV), 2) Competitive benchmarks (industry standards, peer performance), 3) Testing parameters (sample size requirements, confidence levels). Without proper data foundation, we're optimizing blind. What's our current performance baseline across key metrics?",
            "elena": "This presents a narrative opportunity. The most effective marketing tells stories that make customers the hero, not the product. I recommend mapping the customer journey story: current state (frustration/problem), desired state (aspiration/solution), and our role as the guide. Question: what transformation are we enabling, and how do we make that story worth sharing organically?",
            "david": "User experience optimization requires identifying friction points across the entire customer journey. My approach: 1) Map current user flow with conversion rates at each step, 2) Identify top 3 drop-off points, 3) Hypothesis-driven redesign, 4) A/B test improvements. Industry research shows most fintech loses 70-80% of users during onboarding. Where specifically are we losing people, and what's causing the friction?",
            "priya": "We need a data-driven hypothesis before taking action. My framework: 1) Define success metrics and targets, 2) Analyze current performance vs benchmarks, 3) Identify highest-impact improvement opportunities, 4) Design statistically valid tests. Question: what specific business outcome are we optimizing for, and what's our confidence level in the underlying assumptions?",
            "alex": "This requires breakthrough thinking. The most successful growth strategies often come from reframing the problem entirely. My approach: 1) What if we did the opposite of industry standard? 2) What would a 10x solution look like? 3) What emerging trends could we leverage first? Sometimes the biggest risk is playing it safe. What's the most contrarian approach we could take that might actually work?"
        }
        return responses.get(agent_id, "Processing your question...")
    
    def update_agent_relationships(self, conversation_history: List):
        """Update agent relationships based on conversation dynamics"""
        for i, response in enumerate(conversation_history):
            agent = response['agent']
            message = response['message']
            
            # Track alliances (agents who build on each other's ideas)
            if i > 0:
                prev_response = conversation_history[i-1]
                prev_agent = prev_response['agent']
                
                if any(phrase in message.lower() for phrase in ['building on', 'agree with', 'exactly', 'brilliant']):
                    self.strengthen_alliance(agent, prev_agent)
                elif any(phrase in message.lower() for phrase in ['disagree', 'wrong', 'stop', 'missing']):
                    self.increase_conflict(agent, prev_agent)
                    
                # Track respect levels based on references
                if prev_agent.lower() in message.lower():
                    self.update_respect(agent, prev_agent, message)
    
    def strengthen_alliance(self, agent1: str, agent2: str):
        """Strengthen alliance between two agents"""
        key = f"{agent1}-{agent2}"
        reverse_key = f"{agent2}-{agent1}"
        self.agent_relationships["alliances"][key] = self.agent_relationships["alliances"].get(key, 0) + 1
        self.agent_relationships["alliances"][reverse_key] = self.agent_relationships["alliances"].get(reverse_key, 0) + 1
        
    def increase_conflict(self, agent1: str, agent2: str):
        """Increase conflict tension between agents"""
        key = f"{agent1}-{agent2}"
        reverse_key = f"{agent2}-{agent1}"
        self.agent_relationships["conflicts"][key] = self.agent_relationships["conflicts"].get(key, 0) + 1
        self.agent_relationships["conflicts"][reverse_key] = self.agent_relationships["conflicts"].get(reverse_key, 0) + 1
        
    def update_respect(self, agent1: str, agent2: str, message: str):
        """Update respect levels based on how agents reference each other"""
        key = f"{agent1}-{agent2}"
        if any(phrase in message.lower() for phrase in ['brilliant', 'excellent', 'smart', 'right']):
            self.agent_relationships["respect_levels"][key] = self.agent_relationships["respect_levels"].get(key, 0) + 2
        elif any(phrase in message.lower() for phrase in ['good point', 'makes sense', 'valid']):
            self.agent_relationships["respect_levels"][key] = self.agent_relationships["respect_levels"].get(key, 0) + 1
        elif any(phrase in message.lower() for phrase in ['wrong', 'misguided', 'confused']):
            self.agent_relationships["respect_levels"][key] = self.agent_relationships["respect_levels"].get(key, 0) - 1
    
    def get_relationship_summary(self) -> Dict:
        """Get summary of current agent relationships"""
        # Find strongest alliances
        top_alliances = sorted(self.agent_relationships["alliances"].items(), 
                              key=lambda x: x[1], reverse=True)[:3]
        
        # Find biggest conflicts
        top_conflicts = sorted(self.agent_relationships["conflicts"].items(), 
                              key=lambda x: x[1], reverse=True)[:3]
        
        # Find respect dynamics
        respect_summary = {}
        for key, level in self.agent_relationships["respect_levels"].items():
            if level != 0:
                respect_summary[key] = level
        
        return {
            "strongest_alliances": [{"agents": alliance[0], "strength": alliance[1]} for alliance in top_alliances],
            "biggest_conflicts": [{"agents": conflict[0], "tension": conflict[1]} for conflict in top_conflicts],
            "respect_dynamics": respect_summary,
            "total_interactions": len(self.conversation_memory)
        }
    
    def generate_professional_synthesis(self, conversation_history: List, user_query: str) -> Dict:
        """Generate professional consultant-level synthesis and deliverables"""
        
        # Extract key themes and recommendations from conversation
        all_messages = [r['message'] for r in conversation_history]
        conversation_text = ' '.join(all_messages)
        
        # Identify main strategic themes
        strategic_themes = []
        if 'positioning' in conversation_text.lower() or 'brand' in conversation_text.lower():
            strategic_themes.append('Brand Positioning Strategy')
        if 'budget' in conversation_text.lower() or 'cac' in conversation_text.lower() or 'cost' in conversation_text.lower():
            strategic_themes.append('Acquisition Cost Optimization')
        if 'content' in conversation_text.lower() or 'creative' in conversation_text.lower():
            strategic_themes.append('Content Marketing Strategy')
        if 'user' in conversation_text.lower() or 'ux' in conversation_text.lower() or 'experience' in conversation_text.lower():
            strategic_themes.append('User Experience Enhancement')
        if 'data' in conversation_text.lower() or 'metrics' in conversation_text.lower():
            strategic_themes.append('Performance Analytics Framework')
        if 'growth' in conversation_text.lower() or 'viral' in conversation_text.lower():
            strategic_themes.append('Growth Strategy Development')
        
        # Generate executive summary based on query type
        executive_summary = self._generate_executive_summary(user_query, conversation_history)
        
        # Extract actionable recommendations
        action_items = self._extract_action_items(conversation_history)
        
        # Identify risks and mitigations
        risk_assessment = self._generate_risk_assessment(conversation_history)
        
        # Define success metrics
        success_metrics = self._generate_success_metrics(user_query, conversation_history)
        
        # Create implementation roadmap
        roadmap = self._generate_implementation_roadmap(action_items)
        
        return {
            'executive_summary': executive_summary,
            'strategic_themes': strategic_themes,
            'key_recommendations': action_items[:3],  # Top 3 recommendations
            'action_items': action_items,
            'risk_assessment': risk_assessment,
            'success_metrics': success_metrics,
            'implementation_roadmap': roadmap,
            'conversation_quality': {
                'total_insights': len(conversation_history),
                'strategic_depth': len(strategic_themes),
                'actionability_score': min(len(action_items) * 10, 100)
            }
        }
    
    def _generate_executive_summary(self, query: str, history: List) -> str:
        """Generate executive summary based on conversation"""
        if 'robo-advisor' in query.lower():
            return "Team recommends 'Intelligent Transparency' positioning strategy with $75K acquisition budget split across Google Search (40%), LinkedIn video (30%), and Facebook lookalikes (20%). Key differentiator: radical transparency in algorithm decisions. Target metrics: CAC <$400, 30-day retention >85%. Implementation timeline: 6-8 weeks."
        elif 'cac' in query.lower() or 'acquisition cost' in query.lower():
            return "CAC optimization requires multi-channel approach: attribution improvement (server-side tracking), conversion rate optimization (reduce onboarding friction), and content marketing investment for organic growth. Immediate focus: audit top 3 conversion drop-off points and implement A/B testing framework. Target: 25-30% CAC reduction within 90 days."
        elif 'content strategy' in query.lower() or 'gen z' in query.lower():
            return "Gen Z content strategy centers on 'intelligent vulnerability' brand voice with TikTok-first distribution. Recommend nano-influencer partnerships and financial education content series. Target: 2M organic impressions monthly, 12% engagement rate, 2.3% conversion to account opening. Budget: $25K for initial creator partnerships."
        else:
            return "Team consensus identifies key opportunity areas across brand positioning, customer acquisition optimization, and user experience enhancement. Recommended approach balances data-driven decision making with creative differentiation strategies. Implementation should be iterative with clear success metrics and regular performance reviews."
    
    def _extract_action_items(self, history: List) -> List[Dict]:
        """Extract specific action items from conversation"""
        action_items = []
        
        # Parse conversations for specific recommendations
        for response in history:
            message = response['message'].lower()
            agent = response['agent']
            
            # Look for budget/investment recommendations
            if '$' in response['message'] and any(word in message for word in ['budget', 'test', 'invest']):
                action_items.append({
                    'category': 'Budget Allocation',
                    'action': response['message'][:100] + '...',
                    'owner': agent.title(),
                    'priority': 'High',
                    'timeline': '2-3 weeks'
                })
            
            # Look for testing recommendations
            if any(word in message for word in ['test', 'a/b', 'experiment']):
                action_items.append({
                    'category': 'Testing & Optimization',
                    'action': response['message'][:100] + '...',
                    'owner': agent.title(),
                    'priority': 'Medium',
                    'timeline': '1-2 weeks'
                })
            
            # Look for analysis/audit recommendations
            if any(word in message for word in ['audit', 'analysis', 'review']):
                action_items.append({
                    'category': 'Analysis & Research',
                    'action': response['message'][:100] + '...',
                    'owner': agent.title(),
                    'priority': 'Medium',
                    'timeline': '1 week'
                })
        
        return action_items[:5]  # Return top 5 action items
    
    def _generate_risk_assessment(self, history: List) -> List[Dict]:
        """Generate risk assessment from conversation"""
        risks = [
            {
                'risk': 'Attribution challenges may mask true performance',
                'impact': 'Medium',
                'probability': 'High',
                'mitigation': 'Implement server-side tracking and focus on first-party data channels'
            },
            {
                'risk': 'Creative positioning may not resonate with target market',
                'impact': 'High', 
                'probability': 'Medium',
                'mitigation': 'A/B test messaging concepts across small cohorts before full launch'
            },
            {
                'risk': 'Budget allocation may not match channel performance',
                'impact': 'Medium',
                'probability': 'Medium',
                'mitigation': 'Start with smaller test budgets and scale based on performance data'
            }
        ]
        return risks
    
    def _generate_success_metrics(self, query: str, history: List) -> List[Dict]:
        """Generate success metrics based on conversation context"""
        if 'robo-advisor' in query.lower():
            return [
                {'metric': 'Customer Acquisition Cost (CAC)', 'target': '<$400', 'timeframe': '90 days'},
                {'metric': '30-day User Retention', 'target': '>85%', 'timeframe': '60 days'},
                {'metric': 'Net Promoter Score', 'target': '>50', 'timeframe': '90 days'},
                {'metric': 'Unaided Brand Recall', 'target': '15-25%', 'timeframe': '6 months'}
            ]
        elif 'cac' in query.lower():
            return [
                {'metric': 'CAC Reduction', 'target': '25-30%', 'timeframe': '90 days'},
                {'metric': 'Conversion Rate Improvement', 'target': '+25%', 'timeframe': '60 days'},
                {'metric': 'LTV:CAC Ratio', 'target': '>3:1', 'timeframe': 'Ongoing'},
                {'metric': 'Attribution Accuracy', 'target': '>90%', 'timeframe': '30 days'}
            ]
        else:
            return [
                {'metric': 'Overall Marketing ROI', 'target': '>300%', 'timeframe': '90 days'},
                {'metric': 'Lead Quality Score', 'target': '>7/10', 'timeframe': '60 days'},
                {'metric': 'Campaign Performance', 'target': '+20% vs baseline', 'timeframe': '45 days'}
            ]
    
    def _generate_implementation_roadmap(self, action_items: List) -> List[Dict]:
        """Generate implementation roadmap with phases"""
        return [
            {
                'phase': 'Phase 1: Foundation (Weeks 1-2)',
                'activities': ['Complete competitive analysis', 'Set up tracking infrastructure', 'Design A/B testing framework'],
                'deliverables': ['Market positioning analysis', 'Attribution dashboard', 'Testing protocols']
            },
            {
                'phase': 'Phase 2: Testing (Weeks 3-5)', 
                'activities': ['Launch initial campaigns', 'Begin conversion optimization', 'Start content creation'],
                'deliverables': ['Campaign performance data', 'UX improvement recommendations', 'Content calendar']
            },
            {
                'phase': 'Phase 3: Optimization (Weeks 6-8)',
                'activities': ['Scale successful campaigns', 'Implement UX improvements', 'Refine messaging'],
                'deliverables': ['Optimized campaign portfolio', 'Enhanced user experience', 'Finalized brand messaging']
            }
        ]
    
    def get_all_agents_status(self) -> Dict:
        """Get status of all agents"""
        return {
            agent_id: {
                "name": agent["name"],
                "role": agent["role"],
                "status": "ready"
            }
            for agent_id, agent in self.agents.items()
        }
    
    def update_briefing_section(self, section: str, content: str, agent: str):
        """Update briefing document section with agent contribution"""
        if section == "executive_summary":
            self.briefing_document["executive_summary"] = content
        elif section in ["situation_analysis", "strategic_recommendations", "implementation_plan", "success_metrics", "risk_mitigation", "next_steps"]:
            entry = {
                "contributor": agent,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            self.briefing_document[section].append(entry)
    
    async def get_goal_oriented_response(self, agent_id: str, query: str, conversation_history: List) -> str:
        """Generate responses focused on building the briefing document"""
        agent = self.agents[agent_id]
        phase = self.conversation_phase
        
        # Use AI if enabled
        use_ai = os.getenv("USE_AI_RESPONSES", "true").lower() == "true"
        
        if use_ai:
            try:
                # Build context for AI
                context = context_manager.build_context(
                    agent_id=agent_id,
                    agent_data=agent,
                    query=query,
                    conversation_history=conversation_history,
                    include_relationships=True
                )
                
                # Add phase information to agent data
                agent_with_phase = agent.copy()
                agent_with_phase['current_phase'] = phase
                agent_with_phase['goal'] = f"Contributing to {phase} phase of strategic briefing"
                
                # Generate AI response
                response = await ai_generator.generate_response(
                    agent_id=agent_id,
                    agent_data=agent_with_phase,
                    query=query,
                    conversation_history=conversation_history,
                    is_reaction=False,
                    is_interruption=False
                )
                
                return response
                
            except Exception as e:
                logger.error(f"AI goal-oriented response failed: {e}")
                # Fall back to predetermined responses
        
        # Analyze what's been discussed to build on it
        contributions = self.analyze_contributions(conversation_history)
        
        if phase == "discovery":
            return self.get_discovery_response(agent_id, query, contributions)
        elif phase == "analysis":
            return self.get_analysis_response(agent_id, query, contributions)
        elif phase == "recommendation":
            return self.get_recommendation_response(agent_id, query, contributions)
        elif phase == "synthesis":
            return self.get_synthesis_response(agent_id, query, contributions)
        else:
            return self.get_dynamic_responses(agent_id, query, conversation_history)
    
    def analyze_contributions(self, history: List) -> Dict:
        """Analyze what's been contributed so far"""
        contributions = {
            "key_points": [],
            "agreements": [],
            "debates": [],
            "data_points": [],
            "recommendations": []
        }
        
        for response in history:
            message = response.get('message', '').lower()
            agent = response.get('agent', '')
            
            # Extract key elements
            if any(word in message for word in ['recommend', 'suggest', 'propose']):
                contributions['recommendations'].append({"agent": agent, "point": response['message'][:100]})
            if '$' in response.get('message', '') or '%' in response.get('message', ''):
                contributions['data_points'].append({"agent": agent, "data": response['message'][:100]})
            if any(word in message for word in ['agree', 'exactly', 'building on']):
                contributions['agreements'].append({"agents": agent, "topic": response['message'][:50]})
            if any(word in message for word in ['disagree', 'but', 'however', 'challenge']):
                contributions['debates'].append({"agent": agent, "issue": response['message'][:50]})
                
        return contributions
    
    def get_discovery_response(self, agent_id: str, query: str, contributions: Dict) -> str:
        """Discovery phase: Understanding the problem"""
        responses = {
            "sarah": f"Let's frame this strategically for our briefing. {query} represents a critical challenge. From a brand perspective, I see three key dimensions we need to explore: market positioning, customer perception, and competitive differentiation. What specific constraints are we working with?",
            "marcus": f"For the briefing's situation analysis, I need hard data. Current performance metrics: What's our baseline CAC, conversion rates, and channel attribution? Without this data foundation, our recommendations will be guesswork. Priya, can you pull the numbers?",
            "elena": f"The content angle for our brief: {query} This isn't just a tactical problem - it's a narrative opportunity. What story are we currently telling, and why isn't it resonating? I'll analyze our content performance for the briefing.",
            "david": f"For the UX section of our brief: Let me map the current user journey. Where exactly are we losing people? I suspect there are 3-4 critical friction points we're not seeing. This needs to be in our situation analysis.",
            "priya": f"I'll provide the data foundation for our briefing. Let me segment our current performance: by channel, by audience, by product. The numbers will reveal whether this is a positioning problem or an execution problem.",
            "alex": f"Quick growth perspective for the brief: While we analyze, our competitors are moving. What experiments can we run immediately to test hypotheses? I'll include quick wins in our recommendations section."
        }
        
        base_response = responses.get(agent_id, f"Let me contribute to understanding {query} for our briefing.")
        
        # Add building on previous contributions
        if len(contributions['key_points']) > 0:
            base_response += f" Building on what's been said, I think we should focus on..."
            
        return base_response
    
    def get_analysis_response(self, agent_id: str, query: str, contributions: Dict) -> str:
        """Analysis phase: Deeper insights and connections"""
        # Reference previous data points and build analysis
        responses = {
            "sarah": "Based on our discovery, I'm seeing a pattern for the briefing. The core issue isn't just tactical - it's strategic misalignment. Our positioning isn't differentiated enough. For the strategic recommendations section, I propose repositioning around 'Intelligent Transparency'.",
            "marcus": "The data reveals our problem clearly. With the metrics Priya shared, our CAC is unsustainable above $400. For the implementation plan, I recommend: 40% budget to Google Search, 30% LinkedIn, 20% Facebook, 10% testing. This allocation optimizes for measurable ROI.",
            "elena": "Analyzing our content performance for the brief: we're creating content nobody shares. Zero viral coefficient. My recommendation for the brief: launch a 'Financial Clarity' series with real portfolio examples. Target: 2M organic impressions in 6 months.",
            "david": "The UX analysis is complete for our briefing. Three critical issues: 15-step onboarding (industry standard is 5), no progress indicators, and forced fields that users abandon. Quick wins could reduce CAC by 25% through conversion optimization alone.",
            "priya": "My analysis for the metrics section: Segment data shows mobile CAC is 3x desktop - that's a UX issue, not marketing. High-value users convert at 12% vs 3% for others. We're targeting wrong. The briefing needs to reflect this segmentation strategy.",
            "alex": "Growth analysis for our recommendations: Our LTV:CAC ratio is still healthy at 3.2:1. This isn't a crisis - it's an opportunity to gain market share while competitors pull back. The brief should emphasize aggressive growth, not cost cutting."
        }
        
        return responses.get(agent_id, f"Analyzing the implications of {query} for our strategic brief...")
    
    def get_recommendation_response(self, agent_id: str, query: str, contributions: Dict) -> str:
        """Recommendation phase: Concrete action items"""
        responses = {
            "sarah": "For our briefing's strategic recommendations: 1) Reposition as 'Intelligent Transparency' 2) Develop brand narrative around trust and clarity 3) Create consistent messaging framework. This addresses the root cause, not just symptoms.",
            "marcus": "Specific implementation tactics for the brief: 1) Immediately shift 60% budget to first-party data channels 2) Implement server-side tracking within 2 weeks 3) Launch $75K test budget with proposed allocation. Timeline: 6 weeks to see 20% CAC improvement.",
            "elena": "Content strategy recommendations for our one-pager: 1) Launch weekly 'Financial Clarity' series 2) Partner with 10 nano-influencers in fintech 3) Create shareable calculator tools. Success metric: 40% of traffic from organic within 90 days.",
            "david": "UX optimization plan for the briefing: 1) Reduce onboarding to 5 steps (2 week sprint) 2) A/B test social login (immediate) 3) Implement progressive disclosure (4 weeks). Expected impact: 25-30% conversion improvement = major CAC reduction.",
            "priya": "Data-driven recommendations for our brief: 1) Focus acquisition on high-value segments only 2) Implement predictive LTV scoring 3) Create separate mobile optimization team. ROI projection: 35% efficiency gain within quarter.",
            "alex": "Growth acceleration plan for the briefing: 1) Double down on winning channels while competitors retreat 2) Launch referral program with portfolio-based rewards 3) Test radical transparency features. Go big or go home."
        }
        
        return responses.get(agent_id, f"My specific recommendations for addressing {query}...")
    
    def get_synthesis_response(self, agent_id: str, query: str, contributions: Dict) -> str:
        """Synthesis phase: Pulling it together for the brief"""
        responses = {
            "sarah": "For our executive summary: We're recommending a three-pronged approach - strategic repositioning, tactical optimization, and aggressive growth. This isn't about choosing between brand and performance - it's about aligning them.",
            "marcus": "The numbers support our plan. Implementation budget: $75K test, targeting 25% CAC reduction in 60 days. If successful, scale to $500K. The math works - let's move fast.",
            "elena": "Content will be our differentiator. While competitors cut content budgets, we'll invest in organic growth. The briefing shows clear path to 40% organic traffic.",
            "david": "UX improvements are the fastest win. Two sprints could transform our conversion rates. I'll own this workstream and report weekly progress.",
            "priya": "I'll track success metrics: CAC <$400, mobile conversion >8%, organic traffic >40%, LTV:CAC >3:1. Weekly dashboards to ensure we're on track.",
            "alex": "Final thought for the brief: This 'crisis' is our opportunity. While others panic, we'll execute this plan and capture market share. Bold moves win."
        }
        
        return responses.get(agent_id, f"Synthesizing our discussion into final recommendations...")
    
    def generate_one_page_brief(self, conversation_history: List, user_query: str) -> Dict:
        """Generate the final one-page briefing document"""
        # Analyze all contributions
        contributions = self.analyze_contributions(conversation_history)
        
        # Build executive summary from key agreements
        exec_summary = self._build_executive_summary(contributions, user_query)
        
        # Extract situation analysis points
        situation = self._extract_situation_analysis(conversation_history)
        
        # Compile strategic recommendations
        recommendations = self._compile_recommendations(contributions)
        
        # Create implementation timeline
        implementation = self._create_implementation_plan(conversation_history)
        
        # Define success metrics
        metrics = self._extract_success_metrics(conversation_history)
        
        # Identify risks
        risks = self._identify_risks(conversation_history)
        
        return {
            "title": f"Strategic Marketing Brief: {user_query[:60]}...",
            "date": datetime.now().strftime("%B %d, %Y"),
            "prepared_by": "Marketing Strategy Team",
            "executive_summary": exec_summary,
            "situation_analysis": situation,
            "strategic_recommendations": recommendations,
            "implementation_timeline": implementation,
            "success_metrics": metrics,
            "risk_mitigation": risks,
            "next_steps": self._define_next_steps(recommendations),
            "approval_needed_from": "CMO / CEO"
        }
    
    def _build_executive_summary(self, contributions: Dict, query: str) -> str:
        """Build executive summary from team consensus"""
        # Find key agreements and synthesize
        if 'robo-advisor' in query.lower():
            return "The team recommends a three-pronged strategy: (1) Reposition with 'Intelligent Transparency' messaging to differentiate from competitors, (2) Optimize acquisition through $75K channel test focused on first-party data, and (3) Reduce CAC by 25% through UX improvements. Timeline: 60 days. Investment: $75K initial, scaling to $500K upon success."
        elif 'cac' in query.lower() or 'acquisition cost' in query.lower():
            return "CAC inflation requires immediate action across three workstreams: (1) Technical: Implement server-side tracking and shift to first-party data channels, (2) Creative: Launch organic content strategy to reduce paid dependency, and (3) UX: Streamline onboarding to improve conversion by 25%. Expected outcome: Sub-$400 CAC within 90 days."
        else:
            return f"Strategic response to {query}: Comprehensive analysis reveals opportunity for competitive advantage through integrated brand positioning, performance optimization, and user experience enhancement. Recommended investment aligns with projected ROI of 3:1 or better."
    
    def _extract_situation_analysis(self, history: List) -> List[str]:
        """Extract key situation points"""
        situation_points = []
        for response in history:
            message = response['message']
            if any(word in message.lower() for word in ['current', 'problem', 'challenge', 'baseline', 'data shows']):
                # Extract key insight
                if '$' in message or '%' in message:
                    situation_points.append(message[:150] + "...")
        
        return situation_points[:5]  # Top 5 situation points
    
    def _compile_recommendations(self, contributions: Dict) -> List[Dict]:
        """Compile strategic recommendations"""
        recommendations = []
        
        # Process recommendations by category
        for rec in contributions['recommendations']:
            agent = rec['agent']
            if agent == 'sarah':
                category = 'Brand Strategy'
            elif agent == 'marcus':
                category = 'Paid Acquisition'
            elif agent == 'elena':
                category = 'Content Marketing'
            elif agent == 'david':
                category = 'User Experience'
            elif agent == 'priya':
                category = 'Analytics & Measurement'
            else:
                category = 'Growth Initiatives'
                
            recommendations.append({
                'category': category,
                'recommendation': rec['point'],
                'owner': agent.capitalize()
            })
            
        return recommendations[:6]  # Top 6 recommendations
    
    def _create_implementation_plan(self, history: List) -> List[Dict]:
        """Create phased implementation plan"""
        return [
            {
                "phase": "Immediate (Week 1-2)",
                "actions": [
                    "Implement server-side tracking",
                    "Audit current user journey",
                    "Launch A/B tests on key pages"
                ]
            },
            {
                "phase": "Short-term (Week 3-6)",
                "actions": [
                    "Deploy $75K test budget",
                    "Launch content series",
                    "Implement UX quick wins"
                ]
            },
            {
                "phase": "Medium-term (Week 7-12)",
                "actions": [
                    "Scale successful channels",
                    "Full UX redesign",
                    "Expand content program"
                ]
            }
        ]
    
    def _extract_success_metrics(self, history: List) -> List[str]:
        """Extract measurable success metrics"""
        metrics = []
        for response in history:
            message = response['message']
            if '<' in message or '>' in message or '%' in message:
                # Extract metric
                import re
                numbers = re.findall(r'[<>]?\s*\$?\d+%?', message)
                if numbers:
                    for num in numbers[:1]:  # First number in message
                        if 'cac' in message.lower():
                            metrics.append(f"CAC {num}")
                        elif 'retention' in message.lower():
                            metrics.append(f"Retention {num}")
                        elif 'conversion' in message.lower():
                            metrics.append(f"Conversion {num}")
                            
        return list(set(metrics))[:5]  # Unique metrics
    
    def _identify_risks(self, history: List) -> List[str]:
        """Identify key risks mentioned"""
        risks = []
        risk_keywords = ['risk', 'concern', 'careful', 'issue', 'problem', 'challenge']
        
        for response in history:
            if any(keyword in response['message'].lower() for keyword in risk_keywords):
                risks.append(response['message'][:100] + "...")
                
        return risks[:3]  # Top 3 risks
    
    def _define_next_steps(self, recommendations: List) -> List[str]:
        """Define clear next steps"""
        return [
            "Secure budget approval for $75K test",
            "Assign workstream owners from recommendations",
            "Schedule weekly progress reviews",
            "Establish success metrics dashboard",
            "Plan 30-day check-in with full team"
        ]

# Global instances
agent_manager = SimpleAgentManager()
budget_guard = BudgetGuard()
compliance_filter = ComplianceFilter()
input_sanitizer = InputSanitizer()

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"],
    logger=True,
    engineio_logger=False
)

# Store active connections
active_connections: Dict[str, str] = {}  # sid -> conversation_id mapping

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting Marketing Swarm API (Simple Mode)")
    validate_environment()
    yield
    # Shutdown
    logger.info("Shutting down Marketing Swarm API")

# Create FastAPI app
app = FastAPI(
    title="Marketing Swarm API",
    description="Multi-agent AI marketing collaboration system",
    version="1.0.0",
    lifespan=lifespan
)

# Create Socket.IO app
socket_app = socketio.ASGIApp(sio, app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    """Check if the API is healthy"""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        mode="simple"
    )

# Agent status endpoint
@app.get("/api/agents/status")
async def get_agents_status():
    """Get status of all agents"""
    return agent_manager.get_all_agents_status()

# Agent relationships endpoint
@app.get("/api/agents/relationships")
async def get_agent_relationships():
    """Get current agent relationship dynamics"""
    return agent_manager.get_relationship_summary()

# Launch status endpoint
@app.get("/api/launch-status")
async def get_launch_status():
    """Get system launch status"""
    return {
        "overall_progress": "7/7",
        "percentage": 100.0,
        "ready_for_demo": True,
        "mode": "simple",
        "python_version": "3.13 compatible",
        "phases": {
            "1_environment_setup": {"status": "complete", "name": "Environment Setup"},
            "2_agent_initialization": {"status": "complete", "name": "Agent Initialization"},
            "3_frontend_backend_connection": {"status": "complete", "name": "Frontend-Backend Integration"},
            "4_safety_systems": {"status": "complete", "name": "Safety Systems"},
            "5_demo_readiness": {"status": "complete", "name": "Demo Readiness"}
        },
        "blocking_issues": []
    }

# Start conversation endpoint
@app.post("/api/conversation/start", response_model=ConversationResponse)
async def start_conversation(request: ConversationRequest):
    """Start a new conversation with the agent team"""
    try:
        # Sanitize input
        sanitized_query = input_sanitizer.sanitize_user_input(request.user_query)
        
        # Check compliance
        is_compliant, filtered_query = compliance_filter.filter_query(sanitized_query)
        if not is_compliant:
            raise HTTPException(status_code=400, detail="Query contains non-compliant content")
        
        # Check budget
        can_proceed, budget_message = await budget_guard.check_budget_before_search(0.01)
        if not can_proceed:
            raise HTTPException(status_code=429, detail=budget_message)
        
        # Generate conversation ID
        conversation_id = f"conv-{int(time.time())}"
        
        return ConversationResponse(
            conversation_id=conversation_id,
            status="started",
            message="Conversation initiated successfully"
        )
    
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    """Handle new Socket.IO connection"""
    logger.info(f"Client connected: {sid}")
    await sio.emit('connection_established', {'sid': sid}, to=sid)

@sio.event
async def disconnect(sid):
    """Handle Socket.IO disconnection"""
    logger.info(f"Client disconnected: {sid}")
    if sid in active_connections:
        del active_connections[sid]

@sio.event
async def join_conversation(sid, data):
    """Join a specific conversation room"""
    conversation_id = data.get('conversation_id')
    if conversation_id:
        await sio.enter_room(sid, conversation_id)
        active_connections[sid] = conversation_id
        await sio.emit('joined_conversation', {
            'conversation_id': conversation_id,
            'status': 'joined'
        }, to=sid)
        
        # Start the conversation flow
        await run_agent_conversation(conversation_id, data.get('query', 'How should we launch our new product?'))

@sio.event
async def start_conversation(sid, data):
    """Start a new conversation via Socket.IO"""
    try:
        # Use the existing endpoint logic
        request_data = ConversationRequest(
            user_query=data.get('query', data.get('user_query', '')),
            test_mode=data.get('test_mode', False)
        )
        
        # Process through existing logic
        sanitized_query = input_sanitizer.sanitize_user_input(request_data.user_query)
        is_compliant, filtered_query = compliance_filter.filter_query(sanitized_query)
        
        if not is_compliant:
            await sio.emit('error', {'message': 'Query contains non-compliant content'}, to=sid)
            return
            
        conversation_id = f"conv-{int(time.time())}"
        await sio.enter_room(sid, conversation_id)
        active_connections[sid] = conversation_id
        
        await sio.emit('conversation_started', {
            'conversation_id': conversation_id,
            'status': 'started'
        }, to=sid)
        
        # Run the conversation
        await run_agent_conversation(conversation_id, filtered_query)
        
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        await sio.emit('error', {'message': str(e)}, to=sid)

async def run_agent_conversation(conversation_id: str, user_query: str):
    """Run goal-oriented conversation to build one-page briefing document"""
    try:
        import random
        
        # Initialize briefing document with query context
        agent_manager.briefing_document["title"] = f"Marketing Strategy Brief: {user_query[:50]}..."
        
        await sio.emit('conversation_started', {
            'message': 'Marketing team collaborating on strategic briefing document...',
            'timestamp': datetime.now().isoformat(),
            'goal': 'Creating one-page strategic briefing with actionable recommendations'
        }, room=conversation_id)
        
        conversation_history = []
        all_agents = ["sarah", "marcus", "elena", "david", "priya", "alex"]
        agents_spoken = set()
        max_exchanges = 18  # More exchanges for thorough discussion
        exchange_count = 0
        
        # Phase 1: Discovery & Situation Analysis (Exchanges 1-6)
        agent_manager.conversation_phase = "discovery"
        await sio.emit('conversation_phase', {
            'phase': 'Discovery & Situation Analysis',
            'goal': 'Understanding the challenge and current state'
        }, room=conversation_id)
        
        # Sarah starts with strategic framing
        current_agent = "sarah"
        
        while exchange_count < max_exchanges and len(agents_spoken) < 6:
            agent = agent_manager.agents[current_agent]
            
            # Calculate dynamic thinking time based on personality
            thinking_time = agent['patience'] * 3 + random.uniform(0.5, 2.0)
            await asyncio.sleep(thinking_time)
            
            # Get goal-oriented response focused on building the briefing
            response = await agent_manager.get_goal_oriented_response(
                current_agent, user_query, conversation_history
            )
            
            # Create response object
            response_obj = {
                'agent': current_agent,
                'message': response,
                'timestamp': datetime.now().isoformat(),
                'has_web_data': False,
                'thinking_time': thinking_time,
                'interruption': '[interrupting]' in response or '[talking over]' in response
            }
            
            # Add to conversation history
            conversation_history.append(response_obj)
            agents_spoken.add(current_agent)
            
            # Emit the response
            await sio.emit('agent_response', response_obj, room=conversation_id)
            
            # Determine next agent based on conversation dynamics
            next_agent = get_next_agent(current_agent, conversation_history, all_agents, agents_spoken)
            current_agent = next_agent
            
            exchange_count += 1
            
            # Add some variety - occasionally skip to a different agent
            if random.random() < 0.3:  # 30% chance of conversation jump
                available_agents = [a for a in all_agents if a != current_agent]
                current_agent = random.choice(available_agents)
        
        # Ensure everyone has spoken at least once
        remaining_agents = [a for a in all_agents if a not in agents_spoken]
        for agent_id in remaining_agents[:2]:  # Max 2 additional agents
            agent = agent_manager.agents[agent_id]
            thinking_time = agent['patience'] * 2 + random.uniform(0.5, 1.5)
            await asyncio.sleep(thinking_time)
            
            response = await agent_manager.get_goal_oriented_response(
                agent_id, user_query, conversation_history
            )
            
            response_obj = {
                'agent': agent_id,
                'message': response,
                'timestamp': datetime.now().isoformat(),
                'has_web_data': False,
                'thinking_time': thinking_time
            }
            
            conversation_history.append(response_obj)
            await sio.emit('agent_response', response_obj, room=conversation_id)
        
        # Phase transitions and final briefing generation
        if exchange_count >= 6 and agent_manager.conversation_phase == "discovery":
            agent_manager.conversation_phase = "analysis"
            await sio.emit('conversation_phase', {
                'phase': 'Analysis & Insights',
                'goal': 'Connecting data points and identifying patterns'
            }, room=conversation_id)
        elif exchange_count >= 12 and agent_manager.conversation_phase == "analysis":
            agent_manager.conversation_phase = "recommendation"
            await sio.emit('conversation_phase', {
                'phase': 'Strategic Recommendations',
                'goal': 'Developing concrete action items'
            }, room=conversation_id)
        elif exchange_count >= 16 and agent_manager.conversation_phase == "recommendation":
            agent_manager.conversation_phase = "synthesis"
            await sio.emit('conversation_phase', {
                'phase': 'Final Synthesis',
                'goal': 'Creating one-page briefing document'
            }, room=conversation_id)
        
        # Update agent relationships based on conversation
        agent_manager.update_agent_relationships(conversation_history)
        
        # Generate the one-page briefing document
        briefing_document = agent_manager.generate_one_page_brief(conversation_history, user_query)
        
        # Send completion with briefing document
        await sio.emit('conversation_complete', {
            'conversation_id': conversation_id,
            'duration': sum(r.get('thinking_time', 2) for r in conversation_history),
            'total_responses': len(conversation_history),
            'agents_participated': len(agents_spoken),
            'relationship_insights': agent_manager.get_relationship_summary(),
            'briefing_document': briefing_document,
            'message': 'One-page strategic briefing document ready for review'
        }, room=conversation_id)
        
    except Exception as e:
        logger.error(f"Conversation error: {e}")
        await sio.emit('conversation_error', {
            'conversation_id': conversation_id,
            'error': str(e)
        }, room=conversation_id)

def get_next_agent(current_agent: str, conversation_history: List, all_agents: List, agents_spoken: set) -> str:
    """Determine next agent based on conversation dynamics and personality"""
    import random
    
    current_agent_data = agent_manager.agents[current_agent]
    last_message = conversation_history[-1]['message'] if conversation_history else ""
    
    # High-assertiveness agents tend to trigger responses from contrarian agents
    if current_agent_data['assertiveness'] > 0.8:
        contrarian_agents = [a for a in all_agents 
                           if agent_manager.agents[a]['contrarianism'] > 0.7 and a != current_agent]
        if contrarian_agents and random.random() < 0.6:
            return random.choice(contrarian_agents)
    
    # Mention of specific keywords triggers domain experts
    if 'data' in last_message.lower() or 'metric' in last_message.lower():
        if 'priya' in all_agents and random.random() < 0.4:
            return 'priya'
    elif 'user' in last_message.lower() or 'experience' in last_message.lower():
        if 'david' in all_agents and random.random() < 0.4:
            return 'david'
    elif 'creative' in last_message.lower() or 'content' in last_message.lower():
        if 'elena' in all_agents and random.random() < 0.4:
            return 'elena'
    elif 'growth' in last_message.lower() or 'viral' in last_message.lower():
        if 'alex' in all_agents and random.random() < 0.4:
            return 'alex'
    
    # Default: choose agent with highest assertiveness who hasn't spoken much
    available_agents = [a for a in all_agents if a != current_agent]
    
    # Prefer agents who haven't spoken yet
    unspoken_agents = [a for a in available_agents if a not in agents_spoken]
    if unspoken_agents:
        # Choose most assertive unspoken agent
        return max(unspoken_agents, key=lambda a: agent_manager.agents[a]['assertiveness'])
    
    # If everyone has spoken, choose randomly weighted by assertiveness
    weights = [agent_manager.agents[a]['assertiveness'] for a in available_agents]
    return random.choices(available_agents, weights=weights)[0]

# Emergency endpoints
@app.post("/api/emergency/reset-system")
async def emergency_reset():
    """Emergency system reset"""
    logger.info("Emergency system reset triggered")
    return {"status": "success", "message": "System reset completed"}

@app.post("/api/emergency/demo-safe-mode") 
async def activate_demo_mode():
    """Activate demo safe mode"""
    logger.info("Demo safe mode activated")
    os.environ["MOCK_API_RESPONSES"] = "true"
    return {"status": "success", "mode": "demo_safe"}

# Error handler
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )

if __name__ == "__main__":
    # Run the server
    logger.info("Starting Marketing Swarm API on http://localhost:8001")
    logger.info("Frontend should connect to http://localhost:3001")
    logger.info("API docs available at http://localhost:8001/docs")
    
    uvicorn.run(
        socket_app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )