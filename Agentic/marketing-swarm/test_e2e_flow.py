#!/usr/bin/env python3
"""
End-to-End Flow Test for Marketing Swarm
Tests the complete conversation flow from start to finish
"""

import asyncio
import json
import time
from datetime import datetime
import aiohttp
import socketio
from typing import Dict, List

class E2EFlowTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "flows": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0
            }
        }
        
    def record_flow(self, flow_name: str, passed: bool, details: Dict):
        """Record flow test result"""
        self.results["flows"][flow_name] = {
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results["summary"]["total"] += 1
        if passed:
            self.results["summary"]["passed"] += 1
        else:
            self.results["summary"]["failed"] += 1
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\n{status} - {flow_name}")
        if details:
            for key, value in details.items():
                print(f"    {key}: {value}")

    async def test_simple_conversation_flow(self):
        """Test a simple conversation flow"""
        print("\n🔍 Testing Simple Conversation Flow...")
        
        flow_details = {
            "start_time": datetime.now().isoformat(),
            "steps_completed": []
        }
        
        try:
            # Step 1: Start conversation via API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/conversation/start",
                    json={"user_query": "How should we launch our robo-advisor?", "test_mode": True},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to start conversation: HTTP {response.status}")
                    
                    data = await response.json()
                    conversation_id = data.get("conversation_id")
                    if not conversation_id:
                        raise Exception("No conversation ID returned")
                    
                    flow_details["conversation_id"] = conversation_id
                    flow_details["steps_completed"].append("API conversation start")
            
            # Step 2: Connect WebSocket and join conversation
            sio = socketio.AsyncClient()
            events_received = []
            agent_responses = []
            phases = []
            
            @sio.event
            async def connect():
                flow_details["steps_completed"].append("WebSocket connected")
                await sio.emit("join_conversation", {
                    "conversation_id": conversation_id,
                    "query": "How should we launch our robo-advisor?"
                })
            
            @sio.event
            async def joined_conversation(data):
                flow_details["steps_completed"].append("Joined conversation")
                events_received.append("joined_conversation")
            
            @sio.event
            async def phase(data):
                phases.append(data["phase"])
                events_received.append(f"phase:{data['phase']}")
            
            @sio.event
            async def agent_response(data):
                agent_responses.append({
                    "agent": data["agent"],
                    "timestamp": data.get("timestamp"),
                    "message_preview": data.get("message", "")[:100] + "..."
                })
                events_received.append(f"response:{data['agent']}")
            
            @sio.event
            async def conversation_complete(data):
                flow_details["steps_completed"].append("Conversation completed")
                flow_details["duration"] = data.get("duration")
                flow_details["total_responses"] = data.get("total_responses")
                events_received.append("conversation_complete")
            
            # Connect and wait for conversation to complete
            await sio.connect(self.base_url)
            
            # Wait for completion or timeout
            start_time = time.time()
            timeout = 60  # 60 seconds timeout
            
            while "conversation_complete" not in events_received and (time.time() - start_time) < timeout:
                await asyncio.sleep(0.5)
            
            await sio.disconnect()
            
            # Analyze results
            flow_details["websocket_events"] = len(events_received)
            flow_details["agent_responses"] = len(agent_responses)
            flow_details["phases"] = phases
            flow_details["agents_who_responded"] = list(set(r["agent"] for r in agent_responses))
            
            # Check success criteria
            success = all([
                len(phases) >= 3,  # Should have analysis, collaboration, synthesis
                len(agent_responses) >= 6,  # At least 6 agent responses
                "conversation_complete" in events_received
            ])
            
            flow_details["end_time"] = datetime.now().isoformat()
            self.record_flow("Simple Conversation Flow", success, flow_details)
            
        except Exception as e:
            flow_details["error"] = str(e)
            flow_details["end_time"] = datetime.now().isoformat()
            self.record_flow("Simple Conversation Flow", False, flow_details)

    async def test_concurrent_conversations(self):
        """Test multiple concurrent conversations"""
        print("\n🔍 Testing Concurrent Conversations...")
        
        flow_details = {
            "conversations_started": 0,
            "conversations_completed": 0,
            "errors": []
        }
        
        async def run_conversation(index: int):
            try:
                async with aiohttp.ClientSession() as session:
                    # Start conversation
                    async with session.post(
                        f"{self.base_url}/api/conversation/start",
                        json={"user_query": f"Test concurrent conversation {index}", "test_mode": True},
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            flow_details["conversations_started"] += 1
                            data = await response.json()
                            return data.get("conversation_id")
                        else:
                            flow_details["errors"].append(f"Conv {index}: HTTP {response.status}")
                            return None
            except Exception as e:
                flow_details["errors"].append(f"Conv {index}: {str(e)}")
                return None
        
        try:
            # Start 3 concurrent conversations
            tasks = [run_conversation(i) for i in range(3)]
            conversation_ids = await asyncio.gather(*tasks)
            
            # Count successful starts
            successful_ids = [cid for cid in conversation_ids if cid is not None]
            flow_details["successful_starts"] = len(successful_ids)
            
            success = flow_details["conversations_started"] >= 2  # At least 2 should work
            
            self.record_flow("Concurrent Conversations", success, flow_details)
            
        except Exception as e:
            flow_details["error"] = str(e)
            self.record_flow("Concurrent Conversations", False, flow_details)

    async def test_conversation_phases(self):
        """Test that all conversation phases execute correctly"""
        print("\n🔍 Testing Conversation Phases...")
        
        flow_details = {
            "phases_expected": ["analysis", "collaboration", "synthesis"],
            "phases_received": [],
            "phase_timings": {}
        }
        
        try:
            # Start conversation
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/conversation/start",
                    json={"user_query": "Test phase execution", "test_mode": True},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    data = await response.json()
                    conversation_id = data.get("conversation_id")
            
            # Monitor phases via WebSocket
            sio = socketio.AsyncClient()
            phase_start_times = {}
            
            @sio.event
            async def connect():
                await sio.emit("join_conversation", {
                    "conversation_id": conversation_id,
                    "query": "Test phase execution"
                })
            
            @sio.event
            async def phase(data):
                phase_name = data["phase"]
                flow_details["phases_received"].append(phase_name)
                phase_start_times[phase_name] = time.time()
                
                # Calculate duration of previous phase
                if len(flow_details["phases_received"]) > 1:
                    prev_phase = flow_details["phases_received"][-2]
                    duration = phase_start_times[phase_name] - phase_start_times[prev_phase]
                    flow_details["phase_timings"][prev_phase] = f"{duration:.1f}s"
            
            @sio.event
            async def conversation_complete(data):
                # Calculate last phase duration
                if flow_details["phases_received"]:
                    last_phase = flow_details["phases_received"][-1]
                    duration = time.time() - phase_start_times[last_phase]
                    flow_details["phase_timings"][last_phase] = f"{duration:.1f}s"
            
            await sio.connect(self.base_url)
            
            # Wait for completion
            await asyncio.sleep(35)  # Should complete within 35 seconds
            await sio.disconnect()
            
            # Check if all expected phases were received
            all_phases_received = all(
                phase in flow_details["phases_received"] 
                for phase in flow_details["phases_expected"]
            )
            
            flow_details["all_phases_executed"] = all_phases_received
            
            self.record_flow("Conversation Phases", all_phases_received, flow_details)
            
        except Exception as e:
            flow_details["error"] = str(e)
            self.record_flow("Conversation Phases", False, flow_details)

    async def test_agent_participation(self):
        """Test that all agents participate in conversations"""
        print("\n🔍 Testing Agent Participation...")
        
        flow_details = {
            "expected_agents": ["sarah", "marcus", "elena", "david", "priya", "alex"],
            "agents_responded": set(),
            "response_counts": {}
        }
        
        try:
            # Start conversation
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/conversation/start",
                    json={"user_query": "Need comprehensive marketing strategy", "test_mode": True},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    data = await response.json()
                    conversation_id = data.get("conversation_id")
            
            # Monitor agent responses
            sio = socketio.AsyncClient()
            
            @sio.event
            async def connect():
                await sio.emit("join_conversation", {
                    "conversation_id": conversation_id,
                    "query": "Need comprehensive marketing strategy"
                })
            
            @sio.event
            async def agent_response(data):
                agent_name = data["agent"]
                flow_details["agents_responded"].add(agent_name)
                flow_details["response_counts"][agent_name] = \
                    flow_details["response_counts"].get(agent_name, 0) + 1
            
            await sio.connect(self.base_url)
            await asyncio.sleep(35)  # Wait for conversation
            await sio.disconnect()
            
            # Convert set to list for JSON serialization
            flow_details["agents_responded"] = list(flow_details["agents_responded"])
            
            # Check if all agents participated
            all_agents_participated = all(
                agent in flow_details["agents_responded"]
                for agent in flow_details["expected_agents"]
            )
            
            flow_details["all_agents_participated"] = all_agents_participated
            flow_details["total_responses"] = sum(flow_details["response_counts"].values())
            
            self.record_flow("Agent Participation", all_agents_participated, flow_details)
            
        except Exception as e:
            flow_details["error"] = str(e)
            flow_details["agents_responded"] = list(flow_details["agents_responded"])
            self.record_flow("Agent Participation", False, flow_details)

    async def run_all_tests(self):
        """Run all E2E flow tests"""
        print("=" * 60)
        print("🧪 Marketing Swarm End-to-End Flow Tests")
        print("=" * 60)
        
        # Run tests
        await self.test_simple_conversation_flow()
        await self.test_concurrent_conversations()
        await self.test_conversation_phases()
        await self.test_agent_participation()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 E2E Test Summary")
        print("=" * 60)
        print(f"Total Flows Tested: {self.results['summary']['total']}")
        print(f"Passed: {self.results['summary']['passed']} ✅")
        print(f"Failed: {self.results['summary']['failed']} ❌")
        
        if self.results['summary']['total'] > 0:
            pass_rate = (self.results['summary']['passed'] / self.results['summary']['total']) * 100
            print(f"Pass Rate: {pass_rate:.1f}%")
        
        # Save results
        with open('test_results_e2e.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to test_results_e2e.json")
        
        return 0 if self.results['summary']['failed'] == 0 else 1

async def main():
    tester = E2EFlowTester()
    return await tester.run_all_tests()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)