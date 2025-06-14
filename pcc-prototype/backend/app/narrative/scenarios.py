"""
Pre-configured demo scenarios for different audiences
"""

DEMO_SCENARIOS = {
    "morning_surge": {
        "name": "Morning Surge Excellence",
        "duration_minutes": 60,
        "description": "Showcases intelligent capacity management during ED surge",
        "initial_occupancy": 0.85,
        "ed_pressure": "high",
        "scripted_events": [
            {
                "time_minutes": 5,
                "trigger": "ED Alert",
                "description": "Multi-vehicle accident, expecting 6 trauma patients"
            },
            {
                "time_minutes": 10,
                "trigger": "AI Insight",
                "description": "Capacity Predictor identifies 4 probable discharges by noon"
            },
            {
                "time_minutes": 15,
                "trigger": "Discharge Acceleration",
                "description": "AI identifies and resolves PT scheduling conflict for 2 patients"
            },
            {
                "time_minutes": 25,
                "trigger": "Family Coordination",
                "description": "Concierge chat helps coordinate family pickup for early discharge"
            },
            {
                "time_minutes": 35,
                "trigger": "Success Metric",
                "description": "All trauma patients accommodated without delaying care"
            }
        ],
        "showcase_features": [
            "Predictive capacity management",
            "Proactive discharge barrier resolution",
            "Multi-agent coordination",
            "Real-time family communication"
        ],
        "expected_insights": [
            "Hidden discharge opportunities identified",
            "Resource conflicts resolved before they cause delays",
            "Family engagement accelerating discharge"
        ],
        "opening_context": "It's 7:30 AM at St. Mary's Medical Center. The night shift is preparing handoff while the ED is already seeing higher than usual volume. The morning team needs to create capacity quickly.",
        "climax_event": "Multi-casualty incident requires immediate bed availability",
        "resolution": "AI-coordinated discharge acceleration creates needed capacity without compromising care"
    },
    
    "discharge_excellence": {
        "name": "Discharge Barrier Breakthrough",
        "duration_minutes": 45,
        "description": "Demonstrates AI's ability to identify and resolve complex discharge barriers",
        "initial_occupancy": 0.90,
        "ed_pressure": "moderate",
        "scripted_events": [
            {
                "time_minutes": 5,
                "trigger": "Complex Patient",
                "description": "Mrs. Chen - awaiting SNF placement, insurance issues, family concerns"
            },
            {
                "time_minutes": 10,
                "trigger": "AI Analysis",
                "description": "Discharge Accelerator identifies alternative placement options"
            },
            {
                "time_minutes": 15,
                "trigger": "Barrier Resolution",
                "description": "AI suggests home health with family training as alternative"
            },
            {
                "time_minutes": 20,
                "trigger": "Care Coordination",
                "description": "Virtual family meeting coordinated through Concierge Chat"
            },
            {
                "time_minutes": 30,
                "trigger": "Breakthrough",
                "description": "Insurance approval expedited, home health arranged, family confident"
            }
        ],
        "showcase_features": [
            "Complex barrier analysis",
            "Creative solution generation",
            "Stakeholder coordination",
            "Insurance navigation assistance"
        ],
        "expected_insights": [
            "Alternative discharge pathways",
            "Cost-effective solutions",
            "Family engagement strategies"
        ],
        "opening_context": "Several patients have been waiting for discharge for days due to complex social and insurance barriers. The case management team is overwhelmed with the complexity.",
        "climax_event": "Insurance denies SNF coverage for high-need patient",
        "resolution": "AI helps create innovative home-based solution that satisfies all stakeholders"
    },
    
    "night_shift_story": {
        "name": "Night Shift Intelligence",
        "duration_minutes": 40,
        "description": "Shows how AI supports skeleton night crew during critical events",
        "initial_occupancy": 0.80,
        "ed_pressure": "low",
        "scripted_events": [
            {
                "time_minutes": 5,
                "trigger": "Quiet Start",
                "description": "Typical quiet night, reduced staffing per usual"
            },
            {
                "time_minutes": 15,
                "trigger": "Clinical Change",
                "description": "Mr. Johnson in room 302 showing early signs of deterioration"
            },
            {
                "time_minutes": 18,
                "trigger": "AI Alert",
                "description": "Pattern recognition identifies similar symptoms in two other patients"
            },
            {
                "time_minutes": 25,
                "trigger": "Rapid Response",
                "description": "Coordinated intervention prevents three potential ICU transfers"
            },
            {
                "time_minutes": 35,
                "trigger": "Morning Report",
                "description": "Night shift prevented major incident through AI-assisted vigilance"
            }
        ],
        "showcase_features": [
            "Pattern recognition across patients",
            "Early warning system",
            "Resource optimization during low staffing",
            "Predictive intervention"
        ],
        "expected_insights": [
            "Subtle clinical patterns detected",
            "Proactive vs reactive care",
            "Staff force multiplication"
        ],
        "opening_context": "It's 2 AM, and the hospital is running with minimal night staff. Most patients are stable, but the AI systems remain vigilant for any changes.",
        "climax_event": "Multiple patients begin showing similar concerning symptoms",
        "resolution": "AI pattern recognition enables early intervention, preventing crisis"
    },
    
    "executive_overview": {
        "name": "Executive Strategic Impact",
        "duration_minutes": 30,
        "description": "High-level demonstration of ROI and strategic value",
        "initial_occupancy": 0.82,
        "ed_pressure": "moderate",
        "scripted_events": [
            {
                "time_minutes": 5,
                "trigger": "Baseline Metrics",
                "description": "Current state: 4.2 day ALOS, 85% occupancy, $2M monthly revenue"
            },
            {
                "time_minutes": 10,
                "trigger": "AI Optimization",
                "description": "System identifies 15% reduction opportunity in ALOS"
            },
            {
                "time_minutes": 15,
                "trigger": "Financial Impact",
                "description": "Demonstrates $300K monthly revenue opportunity"
            },
            {
                "time_minutes": 20,
                "trigger": "Quality Metrics",
                "description": "Improved patient satisfaction, reduced readmissions"
            },
            {
                "time_minutes": 25,
                "trigger": "Strategic Vision",
                "description": "Pathway to top-decile performance in patient flow"
            }
        ],
        "showcase_features": [
            "Financial ROI modeling",
            "Quality metric improvement",
            "Operational efficiency gains",
            "Strategic competitive advantage"
        ],
        "expected_insights": [
            "Hidden revenue opportunities",
            "Cost reduction pathways",
            "Quality improvement strategies"
        ],
        "opening_context": "St. Mary's Medical Center faces the same challenges as hospitals nationwide: capacity constraints, margin pressure, and quality imperatives. Let's see how AI transforms these challenges into opportunities.",
        "climax_event": "Board pressure to improve margins without adding beds",
        "resolution": "AI demonstrates path to $3.6M annual improvement through flow optimization"
    },
    
    "clinical_excellence": {
        "name": "Clinical Decision Support",
        "duration_minutes": 50,
        "description": "Demonstrates AI supporting complex clinical decisions",
        "initial_occupancy": 0.75,
        "ed_pressure": "moderate",
        "scripted_events": [
            {
                "time_minutes": 5,
                "trigger": "Complex Case",
                "description": "Mr. Rodriguez - multiple comorbidities, conflicting treatment priorities"
            },
            {
                "time_minutes": 12,
                "trigger": "AI Synthesis",
                "description": "System analyzes 200+ similar cases, suggests optimal pathway"
            },
            {
                "time_minutes": 20,
                "trigger": "Team Collaboration",
                "description": "AI facilitates virtual tumor board with remote specialists"
            },
            {
                "time_minutes": 30,
                "trigger": "Family Integration",
                "description": "Concierge chat helps family understand complex treatment plan"
            },
            {
                "time_minutes": 40,
                "trigger": "Outcome",
                "description": "Consensus reached, treatment initiated, family engaged"
            }
        ],
        "showcase_features": [
            "Clinical decision support",
            "Evidence synthesis",
            "Multidisciplinary coordination",
            "Patient/family communication"
        ],
        "expected_insights": [
            "Evidence-based recommendations",
            "Risk stratification",
            "Outcome predictions"
        ],
        "opening_context": "Complex patients often require input from multiple specialists and careful coordination. Today's case demonstrates how AI enhances clinical decision-making without replacing clinical judgment.",
        "climax_event": "Conflicting specialist recommendations create treatment dilemma",
        "resolution": "AI helps synthesize evidence and facilitate consensus"
    }
}