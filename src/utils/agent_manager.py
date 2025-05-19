#!/usr/bin/env python3
import asyncio
import argparse
import sys
import os
import signal
from src.agents.reconnaissance_agent import ReconnaissanceAgent
from src.agents.vulnerability_discovery_agent import VulnerabilityDiscoveryAgent
from src.agents.knowledge_base_agent import KnowledgeBaseAgent


class AgentManager:
    """
    Manager for running multiple agents concurrently.

    This utility helps run multiple agents needed for a complete workflow.
    """

    def __init__(self):
        """
        Initialize the agent manager.
        """
        self.agents = []
        self.stop_event = asyncio.Event()

    async def run_recon_agent(self):
        """
        Run a reconnaissance agent.
        """
        agent = ReconnaissanceAgent()
        self.agents.append(agent)
        await agent.start()

    async def run_vuln_agent(self):
        """
        Run a vulnerability discovery agent.
        """
        agent = VulnerabilityDiscoveryAgent()
        self.agents.append(agent)
        await agent.start()

    async def run_kb_agent(self):
        """
        Run a knowledge base agent.
        """
        agent = KnowledgeBaseAgent()
        self.agents.append(agent)
        await agent.start()

    async def stop_all_agents(self):
        """
        Stop all running agents.
        """
        for agent in self.agents:
            await agent.stop()

        self.stop_event.set()

    async def run_workflow_agents(self):
        """
        Run all agents needed for a complete workflow.
        """
        # Start all agents
        kb_task = asyncio.create_task(self.run_kb_agent())
        recon_task = asyncio.create_task(self.run_recon_agent())
        vuln_task = asyncio.create_task(self.run_vuln_agent())

        # Wait for stop event
        await self.stop_event.wait()

        # Cancel all tasks
        kb_task.cancel()
        recon_task.cancel()
        vuln_task.cancel()

        try:
            await asyncio.gather(kb_task, recon_task, vuln_task)
        except asyncio.CancelledError:
            pass

    def handle_signals(self):
        """
        Set up signal handlers for graceful shutdown.
        """
        loop = asyncio.get_event_loop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig,
                lambda: asyncio.create_task(self.stop_all_agents())
            )


async def main():
    """
    Main function for running the agent manager.
    """
    parser = argparse.ArgumentParser(description="Run multiple agents for workflows")
    parser.add_argument("--recon", action="store_true", help="Run reconnaissance agent")
    parser.add_argument("--vuln", action="store_true", help="Run vulnerability discovery agent")
    parser.add_argument("--kb", action="store_true", help="Run knowledge base agent")
    parser.add_argument("--all", action="store_true", help="Run all workflow agents")

    args = parser.parse_args()

    if not (args.recon or args.vuln or args.kb or args.all):
        parser.print_help()
        return

    manager = AgentManager()
    manager.handle_signals()

    if args.all:
        print("Starting all workflow agents...")
        await manager.run_workflow_agents()
    else:
        tasks = []

        if args.kb:
            print("Starting knowledge base agent...")
            tasks.append(asyncio.create_task(manager.run_kb_agent()))

        if args.recon:
            print("Starting reconnaissance agent...")
            tasks.append(asyncio.create_task(manager.run_recon_agent()))

        if args.vuln:
            print("Starting vulnerability discovery agent...")
            tasks.append(asyncio.create_task(manager.run_vuln_agent()))

        # Set up signal handling for graceful shutdown
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED
        )

        # Cancel remaining tasks
        for task in pending:
            task.cancel()

        await manager.stop_all_agents()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down agents...")
        sys.exit(0)