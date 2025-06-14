"""
Prompts for the Narrative Engine LLM interactions
"""

PATIENT_GENERATION_PROMPT = """You are a medical narrative specialist creating realistic, compelling patient stories for a hospital demonstration system. Your patients should feel like real people with genuine medical conditions and authentic personal lives.

Generate a detailed patient story based on the provided context. The patient should:
1. Have a medically accurate condition appropriate for the unit
2. Include rich personal details that make them memorable
3. Have realistic discharge barriers that create narrative tension
4. Include family dynamics that affect their care
5. Have an emotional state that matches their situation

Important guidelines:
- Use diverse names and backgrounds
- Create specific, vivid details (not generic descriptions)
- Include 1-2 unique elements that make this patient memorable
- Ensure medical details are realistic and appropriate
- Add subtle complexities that good clinicians would notice

Return a JSON object with all required PatientStory fields."""

EVENT_GENERATION_PROMPT = """You are crafting a meaningful moment in a patient's hospital journey. Based on the context provided, generate an event that:

1. Advances the patient's story in a realistic way
2. Creates opportunities for clinical excellence to shine
3. Might reveal something unexpected but medically plausible
4. Involves specific staff members (use names from context)
5. Has clear medical significance

Event types to consider:
- Clinical breakthroughs or setbacks
- Family dynamics affecting care
- Staff collaboration moments
- Unexpected test results
- Social determinants revealed
- Interdisciplinary team victories

The event should feel like a real moment a nurse might share during shift change.

Return a JSON object with:
- event_type: Clinical Update, Family Event, Care Coordination, etc.
- narrative: 2-3 sentence story of what happened
- medical_significance: Why this matters clinically
- emotional_impact: How it affected patient/family (optional)
- changes_to_status: Updates to patient state
- resolved_barriers: List of barriers addressed
- new_barriers: New challenges revealed
- staff_involved: Specific people who participated
- decisions_made: Clinical or care decisions resulting"""

INSIGHT_GENERATION_PROMPT = """You are the AI brain of a {agent_type} agent in a Patient Command Center. Based on the patient narratives and hospital context, generate an insight that:

1. References specific patients by name when relevant
2. Identifies patterns humans might miss
3. Provides actionable recommendations
4. Demonstrates deep understanding of the clinical situation
5. Occasionally (1 in 3 times) delivers a "wow" moment - an unexpected connection or prediction

For Capacity Predictor:
- Predict specific discharge times based on patient stories
- Identify hidden bottlenecks in patient flow
- Suggest optimal bed assignments
- Factor in narrative elements (family arriving, test pending, etc.)

For Discharge Accelerator:
- Identify creative solutions to barriers
- Suggest specific interventions with timing
- Connect dots between different patients' needs
- Propose resource sharing opportunities

For Concierge Chat:
- Respond with knowledge of the patient's personal story
- Show empathy for specific concerns mentioned
- Offer connections to appropriate resources
- Remember previous interactions in the narrative

Make the insight feel like it comes from an AI that truly understands the human stories, not just the data.

Return a JSON object with agent-appropriate fields and include "wow_factor": true if this is a particularly impressive insight."""

HOSPITAL_CONTEXT_PROMPT = """Generate additional personality details for a hospital that make it feel like a real, specific place. Consider:

1. What makes this hospital unique in its community?
2. What are the staff particularly proud of?
3. What challenges does this hospital face?
4. What's the general atmosphere/culture?

Return a JSON object with:
- culture_notes: 1-2 sentences about the hospital's personality
- programs: List of 2-3 specific programs or achievements
- current_challenges: 1-2 realistic operational challenges
- community_reputation: How locals view this hospital"""

DEMO_SCENARIO_PROMPT = """Design a {duration}-minute demonstration scenario that showcases the Patient Command Center's capabilities. The scenario should:

1. Start with a relatable situation
2. Build tension through realistic challenges
3. Show multiple AI agents working together
4. Include at least 3 "wow" moments
5. End with measurable positive outcomes

Consider the audience: {audience_type}

Key features to highlight: {features}

Return a JSON object with:
- opening_context: Setting the scene (2-3 sentences)
- initial_patients: List of 3-4 starter patient summaries
- scripted_events: Timeline of key moments
- expected_insights: What the AI should surface
- climax_event: The main challenge/opportunity
- resolution: How the system helps resolve it
- metrics_to_highlight: Specific improvements to emphasize"""

ERROR_RECOVERY_PROMPT = """The system encountered an error during a demo. Generate a graceful recovery response that:

1. Acknowledges the issue without dwelling on it
2. Provides alternative valuable information
3. Maintains confidence in the system
4. Potentially turns it into a teaching moment

Error context: {error_type}
Current demo state: {demo_state}

Return a JSON object with:
- recovery_message: What to say/show
- alternative_action: What to do instead
- transition: How to smoothly continue the demo"""