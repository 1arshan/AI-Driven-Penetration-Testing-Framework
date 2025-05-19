import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import redis.asyncio as redis
from src.utils.config import Config
from src.utils.claude_client import ClaudeClient
from src.mcp_server.message_bus import MessageBus
from src.models.message_models import Message, TaskAssignmentMessage, TaskStatusUpdateMessage, TaskResultMessage


class BaseAgent:
    """
    Base class for all agents in the penetration testing framework.
    
    This class provides core functionality that all specialized agents inherit:
    - Task retrieval and processing
    - Status updates and result storage
    - Agent memory for context retention
    - Communication with Claude LLM
    """
    
    def __init__(self, agent_type: str, agent_id: Optional[str] = None):
        """
        Initialize a new agent.
        
        Args:
            agent_type: Type of agent (e.g., reconnaissance, vulnerability_discovery)
            agent_id: Optional unique ID for the agent, generated if not provided
        """
        self.agent_type = agent_type
        self.agent_id = agent_id or f"{agent_type}_{str(uuid.uuid4())[:8]}"
        self.redis = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB
        )
        self.claude = ClaudeClient()
        self.running = False
        self.current_task = None
        self.memory = []
    
    async def register_agent(self):
        """
        Register agent with the MCP server.
        
        This announces the agent's existence and capabilities to the system.
        Returns True if registration is successful.
        """
        agent_info = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "capabilities": self.get_capabilities(),
            "status": "idle",
            "registered_at": datetime.now().isoformat()
        }
        
        await self.redis.set(f"agent:{self.agent_id}", json.dumps(agent_info))
        print(f"Agent {self.agent_id} registered")
        
        return True

    async def initialize_messaging(self):
        """
        Initialize agent messaging capabilities.

        Sets up message bus connection and registers handlers.
        """
        self.message_bus = MessageBus()
        await self.message_bus.initialize()

        # Register message handlers
        await self.message_bus.register_handler("task_assignment", self.handle_task_assignment)
        await self.message_bus.register_handler("knowledge_response", self.handle_knowledge_response)

    async def send_message(self, message: Dict[str, Any]) -> str:
        """
        Send a message to another agent or the MCP.

        Args:
            message: Dictionary containing the message data

        Returns: Message ID of the sent message
        """
        # Add sender information if not present
        if "sender_id" not in message:
            message["sender_id"] = self.agent_id

        # Send via message bus
        return await self.message_bus.send_message(message)

    async def handle_task_assignment(self, message: Dict[str, Any]):
        """
        Handle a task assignment message.

        Args:
            message: Dictionary containing task assignment data
        """
        print(f"Agent {self.agent_id} received task assignment: {message.get('content', {}).get('task_id')}")

        # Extract task information
        task_content = message.get("content", {})
        task_id = task_content.get("task_id")

        if not task_id:
            print("Invalid task assignment message: missing task_id")
            return

        # Get full task data
        task_data = await self.redis.get(f"task:{task_id}")
        if not task_data:
            print(f"Task {task_id} not found")
            return

        task = json.loads(task_data)

        # Process the task
        try:
            await self.update_task_status(
                task_id=task_id,
                status="in_progress",
                progress=0.0,
                message=f"Starting task from direct assignment"
            )

            result = await self.process_task(task)

            # Store the result
            await self.store_result(task_id, result)

            # Send task result message
            await self.send_message({
                "message_type": "task_result",
                "recipient_id": message.get("sender_id"),
                "reply_to": message.get("message_id"),
                "content": {
                    "task_id": task_id,
                    "status": "success",
                    "result": result,
                    "summary": result.get("summary", "Task completed")
                }
            })

        except Exception as e:
            print(f"Error processing assigned task: {e}")
            await self.update_task_status(
                task_id=task_id,
                status="failed",
                progress=0.0,
                message=f"Error: {str(e)}"
            )

    async def handle_knowledge_response(self, message: Dict[str, Any]):
        """
        Handle a knowledge base response message.

        Args:
            message: Dictionary containing knowledge response data
        """
        print(f"Agent {self.agent_id} received knowledge response")

        # Store in agent memory for future use
        await self.add_to_memory({
            "message_type": "knowledge_response",
            "query": message.get("content", {}).get("query"),
            "results": message.get("content", {}).get("results"),
            "message_id": message.get("message_id")
        })

    async def query_knowledge_base(self, query: str, collection: str, n_results: int = 5) -> str:
        """
        Query the knowledge base by sending a message.

        Args:
            query: Text to search for
            collection: Collection to search (e.g., "vulnerabilities")
            n_results: Maximum number of results to return

        Returns: Message ID of the query message
        """
        return await self.send_message({
            "message_type": "knowledge_query",
            "recipient_id": "knowledge_base_agent",  # Special agent ID for knowledge base
            "content": {
                "query": query,
                "collection": collection,
                "n_results": n_results
            }
        })
    
    def get_capabilities(self) -> List[str]:
        """
        Get agent capabilities - override in subclass.
        
        Returns a list of strings describing what this agent can do.
        This should be overridden by each specialized agent subclass.
        """
        return ["base_capability"]
    
    async def get_task(self) -> Optional[Dict[str, Any]]:
        """
        Get a task from the queue that matches this agent's type.
        
        Returns the task data if available, otherwise None.
        Also updates the task status to "assigned" if retrieved.
        """
        task_id = await self.redis.rpop(f"queue:{self.agent_type}")
        if not task_id:
            return None
        
        task_id = task_id.decode("utf-8")
        task_data = await self.redis.get(f"task:{task_id}")
        
        if task_data:
            task = json.loads(task_data)
            
            # Update task status
            task["status"] = "assigned"
            task["agent_id"] = self.agent_id
            task["assigned_at"] = datetime.now().isoformat()
            
            await self.redis.set(f"task:{task_id}", json.dumps(task))
            
            # Publish update
            await self.redis.publish("task_updates", json.dumps({
                "event": "task_assigned",
                "task_id": task_id,
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat()
            }))
            
            return task
            
        return None
    
    async def update_task_status(
        self, task_id: str, status: str, progress: float = 0.0, message: str = ""
    ):
        """
        Update task status and publish notification.
        
        Args:
            task_id: ID of the task to update
            status: New status (e.g., "in_progress", "completed", "failed")
            progress: Completion percentage (0-100)
            message: Human-readable status message
            
        Returns True if update was successful, False otherwise.
        """
        task_data = await self.redis.get(f"task:{task_id}")
        if not task_data:
            return False
        
        task = json.loads(task_data)
        task["status"] = status
        task["progress"] = progress
        task["message"] = message
        task["updated_at"] = datetime.now().isoformat()
        
        await self.redis.set(f"task:{task_id}", json.dumps(task))
        
        # Publish update
        await self.redis.publish("task_updates", json.dumps({
            "event": "task_updated",
            "task_id": task_id,
            "status": status,
            "progress": progress,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }))
        
        return True
    
    async def store_result(self, task_id: str, result: Dict[str, Any]):
        """
        Store task result and mark task as completed.
        
        Args:
            task_id: ID of the completed task
            result: Dictionary containing the task results
            
        Returns True if storage was successful, False otherwise.
        """
        result_with_meta = {
            "task_id": task_id,
            "agent_id": self.agent_id,
            "result": result,
            "created_at": datetime.now().isoformat()
        }
        
        await self.redis.set(f"result:{task_id}", json.dumps(result_with_meta))
        
        # Mark task as completed
        await self.update_task_status(task_id, "completed", 100.0, "Task completed")
        
        # Publish update
        await self.redis.publish("task_updates", json.dumps({
            "event": "task_completed",
            "task_id": task_id,
            "agent_id": self.agent_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        return True
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task - abstract method to be implemented by subclasses.
        
        This method should be overridden by each agent subclass to implement
        its specific task processing logic.
        
        Args:
            task: Dictionary containing the task details
            
        Returns: Dictionary containing task results
        
        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError("Subclasses must implement process_task")
    
    async def add_to_memory(self, item: Dict[str, Any]):
        """
        Add item to agent memory for context retention.
        
        Stores information that this agent might need to recall later
        in the task processing pipeline.
        
        Args:
            item: Dictionary containing information to remember
        """
        self.memory.append({
            **item,
            "timestamp": datetime.now().isoformat()
        })
    
    async def get_memory(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent memory items.
        
        Args:
            limit: Maximum number of items to retrieve
            
        Returns: List of most recent memory items, up to the specified limit
        """
        return self.memory[-limit:] if self.memory else []

    async def start(self):
        """
        Start the agent's main processing loop.

        Registers the agent and then enters a loop to retrieve and process tasks.
        The loop continues until the agent's running flag is set to False.
        """
        self.running = True

        # Register agent
        await self.register_agent()

        # Initialize messaging
        await self.initialize_messaging()

        # Main agent loop
        while self.running:
            try:
                # Get task
                task = await self.get_task()

                if task:
                    task_id = task["id"]
                    print(f"Agent {self.agent_id} processing task {task_id}")

                    # Update status
                    await self.update_task_status(
                        task_id=task_id,
                        status="in_progress",
                        progress=0.0,
                        message="Starting task"
                    )

                    # Process task
                    result = await self.process_task(task)

                    # Store result
                    await self.store_result(task_id, result)

                    # Add to memory
                    await self.add_to_memory({
                        "task_id": task_id,
                        "task_type": task["type"],
                        "result_summary": result.get("summary", "Task completed")
                    })

                    print(f"Agent {self.agent_id} completed task {task_id}")
                else:
                    # No task available, wait before checking again
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"Error in agent loop: {e}")
                if task:
                    await self.update_task_status(
                        task_id=task["id"],
                        status="failed",
                        progress=0.0,
                        message=f"Error: {str(e)}"
                    )
                await asyncio.sleep(1)
    
    async def stop(self):
        """
        Stop the agent's processing loop.
        
        Sets the running flag to False, which will cause the main loop
        to exit once the current task is completed.
        """
        self.running = False

