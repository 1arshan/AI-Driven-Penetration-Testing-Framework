import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
import redis.asyncio as redis
from src.utils.config import Config
from src.models.message_models import Message


class MessageBus:
    """
    Message bus for agent communication.

    Handles message routing, storage, and delivery between agents
    in the multi-agent system.
    """

    def __init__(self):
        """
        Initialize the message bus with Redis connection.
        """
        self.redis = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB
        )
        self.pubsub = self.redis.pubsub()
        self.handlers: Dict[str, List[Callable]] = {}

    async def initialize(self):
        """
        Initialize the message bus.

        Sets up Redis pub/sub subscription and starts the message listener.
        """
        await self.pubsub.subscribe("agent_messages")

        # Start listening for messages
        asyncio.create_task(self._message_listener())

    async def send_message(self, message: Dict[str, Any]) -> str:
        """
        Send a message to the bus.

        Args:
            message: Dictionary containing the message data

        Returns: Message ID of the sent message
        """
        # Ensure message has ID and timestamp
        if "message_id" not in message:
            message["message_id"] = str(uuid.uuid4())

        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()

        # Store message in Redis
        await self.redis.set(
            f"message:{message['message_id']}",
            json.dumps(message),
            ex=86400  # Expire after 24 hours
        )

        # Publish notification
        await self.redis.publish("agent_messages", json.dumps({
            "event": "new_message",
            "message_id": message["message_id"],
            "sender_id": message.get("sender_id"),
            "recipient_id": message.get("recipient_id"),
            "message_type": message.get("message_type")
        }))

        return message["message_id"]

    async def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a message by ID.

        Args:
            message_id: ID of the message to retrieve

        Returns: Dictionary with message data if found, None otherwise
        """
        message_data = await self.redis.get(f"message:{message_id}")
        if message_data:
            return json.loads(message_data)
        return None

    async def register_handler(self, message_type: str, handler: Callable):
        """
        Register a handler for a message type.

        Args:
            message_type: Type of message to handle
            handler: Callback function that processes messages of this type
        """
        if message_type not in self.handlers:
            self.handlers[message_type] = []

        self.handlers[message_type].append(handler)

    async def _message_listener(self):
        """
        Listen for messages and dispatch to handlers.

        This method runs in a background task and continuously listens
        for new messages, dispatching them to registered handlers.
        """
        while True:
            try:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True)
                if message and message["type"] == "message":
                    data = json.loads(message["data"].decode("utf-8"))

                    if data.get("event") == "new_message":
                        message_id = data.get("message_id")
                        message_data = await self.get_message(message_id)

                        if message_data:
                            # Dispatch to handlers
                            message_type = message_data.get("message_type")
                            if message_type in self.handlers:
                                for handler in self.handlers[message_type]:
                                    try:
                                        await handler(message_data)
                                    except Exception as e:
                                        print(f"Error in message handler: {e}")

                # Small delay to prevent CPU overuse
                await asyncio.sleep(0.01)
            except Exception as e:
                print(f"Error in message listener: {e}")
                await asyncio.sleep(1)  # Delay before retry

    async def get_messages_for_agent(
            self,
            agent_id: str,
            limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent messages for a specific agent.

        Args:
            agent_id: ID of the agent
            limit: Maximum number of messages to retrieve

        Returns: List of message dictionaries
        """
        message_keys = await self.redis.keys(f"message:*")
        messages = []

        for key in message_keys:
            message_data = await self.redis.get(key)
            if message_data:
                message = json.loads(message_data)
                if message.get("recipient_id") == agent_id or message.get("sender_id") == agent_id:
                    messages.append(message)

        # Sort by timestamp (newest first)
        messages.sort(key=lambda m: m.get("timestamp", ""), reverse=True)

        # Limit number of messages
        return messages[:limit]