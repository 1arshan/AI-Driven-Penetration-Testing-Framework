#!/usr/bin/env python3
import asyncio
import argparse
import sys
import os
from src.agents.reconnaissance_agent import ReconnaissanceAgent
from src.agents.knowledge_base_agent import KnowledgeBaseAgent
from src.agents.vulnerability_discovery_agent import VulnerabilityDiscoveryAgent


async def run_agent(agent_type: str, agent_id: str = None):
    """
    Run an agent of the specified type.

    This starts the agent and begins its task processing loop.

    Args:
        agent_type: Type of agent to run (e.g., "reconnaissance")
        agent_id: Optional unique ID for the agent
    """
    print(f"Starting {agent_type} agent...")

    if agent_type == "reconnaissance":
        agent = ReconnaissanceAgent(agent_id=agent_id)
        await agent.start()
    elif agent_type == "knowledge_base":
        agent = KnowledgeBaseAgent(agent_id=agent_id)
        await agent.start()
    elif agent_type == "vulnerability_discovery":
        agent = VulnerabilityDiscoveryAgent(agent_id=agent_id)
        await agent.start()
    else:
        print(f"Unknown agent type: {agent_type}")
        return

    print(f"{agent_type} agent stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run an agent of the specified type")
    parser.add_argument("--type", default="reconnaissance", help="Agent type to run")
    parser.add_argument("--id", help="Optional agent ID")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(run_agent(args.type, args.id))
    except KeyboardInterrupt:
        print("\nAgent stopped by user")
        sys.exit(0)