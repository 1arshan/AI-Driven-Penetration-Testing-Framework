#!/usr/bin/env python3
import asyncio
import argparse
import json
import sys
import uuid
from datetime import datetime
from src.agents.reconnaissance_agent import ReconnaissanceAgent
from src.agents.knowledge_base_agent import KnowledgeBaseAgent


async def test_agent_communication():
    """
    Test agent-to-agent communication using the message bus.

    This test creates a knowledge base agent and a reconnaissance agent,
    and tests communication between them.
    """
    print("Starting agent communication test...")

    # Create agents
    print("Creating knowledge base agent...")
    kb_agent = KnowledgeBaseAgent()

    print("Creating reconnaissance agent...")
    recon_agent = ReconnaissanceAgent(agent_id="test_recon_agent")

    # Initialize messaging for both agents
    await kb_agent.initialize_messaging()
    await recon_agent.initialize_messaging()

    # Register agents
    await kb_agent.register_agent()
    await recon_agent.register_agent()

    # Wait a moment for initialization
    print("Agents initialized, waiting 2 seconds...")
    await asyncio.sleep(2)

    # Test knowledge query
    print("\nTesting knowledge query from reconnaissance agent to knowledge base agent...")
    query_message_id = await recon_agent.query_knowledge_base(
        query="Apache 2.4.41 vulnerability",
        collection="vulnerabilities",
        n_results=3
    )

    print(f"Sent query message with ID: {query_message_id}")

    # Wait for processing
    print("Waiting 3 seconds for message processing...")
    await asyncio.sleep(3)

    # Check if reconnaissance agent received a response (in memory)
    recon_memory = await recon_agent.get_memory()

    knowledge_responses = [
        item for item in recon_memory
        if item.get("message_type") == "knowledge_response"
    ]

    if knowledge_responses:
        print("\nReconnaissance agent received knowledge response:")
        for response in knowledge_responses:
            print(f"Query: {response.get('query')}")
            results = response.get('results', [])
            print(f"Results: {len(results)} items found")

            for i, result in enumerate(results[:2]):  # Show first 2 results
                print(f"\nResult {i + 1}:")
                if "metadata" in result and "name" in result["metadata"]:
                    print(f"Name: {result['metadata']['name']}")
                if "document" in result:
                    doc = result["document"]
                    print(f"Document: {doc[:150]}..." if len(doc) > 150 else doc)
        print("\nCommunication test successful!")
    else:
        print("\nNo knowledge response received in reconnaissance agent memory")
        print("Communication test failed!")

    # Clean up
    await recon_agent.stop()
    await kb_agent.stop()


if __name__ == "__main__":
    asyncio.run(test_agent_communication())