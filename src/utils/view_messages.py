#!/usr/bin/env python3
import asyncio
import argparse
import json
import sys
from src.mcp_server.message_bus import MessageBus
from src.utils.config import Config


async def view_recent_messages(agent_id=None, limit=10):
    """
    View recent messages in the system.

    Args:
        agent_id: Optional agent ID to filter messages
        limit: Maximum number of messages to display
    """
    print(f"Viewing recent messages{f' for agent {agent_id}' if agent_id else ''}")

    # Initialize message bus
    message_bus = MessageBus()

    try:
        # Get recent messages
        if agent_id:
            messages = await message_bus.get_messages_for_agent(agent_id, limit)
        else:
            # Get all messages (simplified implementation)
            message_keys = await message_bus.redis.keys("message:*")
            messages = []

            for key in message_keys:
                message_data = await message_bus.redis.get(key)
                if message_data:
                    messages.append(json.loads(message_data))

            # Sort by timestamp (newest first)
            messages.sort(key=lambda m: m.get("timestamp", ""), reverse=True)

            # Limit number of messages
            messages = messages[:limit]

        # Display messages
        if messages:
            print(f"\nFound {len(messages)} messages:")
            for i, message in enumerate(messages):
                print(f"\n--- Message {i + 1} ---")
                print(f"ID: {message.get('message_id')}")
                print(f"Type: {message.get('message_type')}")
                print(f"From: {message.get('sender_id')} To: {message.get('recipient_id', 'broadcast')}")
                print(f"Time: {message.get('timestamp')}")

                if message.get('reply_to'):
                    print(f"Reply to: {message.get('reply_to')}")

                print("\nContent:")
                content = message.get("content", {})
                print(json.dumps(content, indent=2))
        else:
            print("No messages found")

    except Exception as e:
        print(f"Error viewing messages: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="View recent agent messages")
    parser.add_argument("--agent", help="Agent ID to filter messages")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of messages to display")

    args = parser.parse_args()

    asyncio.run(view_recent_messages(args.agent, args.limit))