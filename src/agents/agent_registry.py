import asyncio
import json
from typing import Dict, List, Optional, Any
import redis.asyncio as redis
from src.utils.config import Config

class AgentRegistry:
    """
    Registry for managing agent registration and discovery.
    
    This class provides functionality to:
    - Register new agents
    - Track agent status
    - Find agents by type or ID
    - Maintain a central registry of all available agents
    """
    
    def __init__(self):
        """
        Initialize the agent registry with Redis connection.
        """
        self.redis = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB
        )
    
    async def register_agent(self, agent_info: Dict[str, Any]) -> bool:
        """
        Register an agent with the system.
        
        Stores agent information and adds it to the appropriate type set.
        
        Args:
            agent_info: Dictionary containing agent details including ID and type
            
        Returns: True if registration successful, False otherwise
        """
        agent_id = agent_info.get("agent_id")
        if not agent_id:
            return False
        
        # Store agent info
        await self.redis.set(f"agent:{agent_id}", json.dumps(agent_info))
        
        # Add to agent type set
        agent_type = agent_info.get("agent_type", "unknown")
        await self.redis.sadd(f"agents:{agent_type}", agent_id)
        
        return True
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the system.
        
        Removes agent information and from its type set.
        
        Args:
            agent_id: ID of the agent to unregister
            
        Returns: True if unregistration successful, False otherwise
        """
        # Get agent info
        agent_data = await self.redis.get(f"agent:{agent_id}")
        if not agent_data:
            return False
        
        agent_info = json.loads(agent_data)
        agent_type = agent_info.get("agent_type", "unknown")
        
        # Remove from agent type set
        await self.redis.srem(f"agents:{agent_type}", agent_id)
        
        # Remove agent info
        await self.redis.delete(f"agent:{agent_id}")
        
        return True
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent information by ID.
        
        Args:
            agent_id: ID of the agent to retrieve
            
        Returns: Dictionary with agent information or None if not found
        """
        agent_data = await self.redis.get(f"agent:{agent_id}")
        if agent_data:
            return json.loads(agent_data)
        return None
    
    async def get_agents_by_type(self, agent_type: str) -> List[Dict[str, Any]]:
        """
        Get all agents of a specific type.
        
        Args:
            agent_type: Type of agents to retrieve (e.g., "reconnaissance")
            
        Returns: List of dictionaries containing agent information
        """
        agent_ids = await self.redis.smembers(f"agents:{agent_type}")
        agents = []
        
        for agent_id in agent_ids:
            agent_id = agent_id.decode("utf-8")
            agent_info = await self.get_agent(agent_id)
            if agent_info:
                agents.append(agent_info)
        
        return agents
    
    async def get_all_agents(self) -> List[Dict[str, Any]]:
        """
        Get all registered agents.
        
        Returns: List of dictionaries containing all agent information
        """
        agent_keys = await self.redis.keys("agent:*")
        agents = []
        
        for key in agent_keys:
            agent_id = key.decode("utf-8").split(":", 1)[1]
            agent_info = await self.get_agent(agent_id)
            if agent_info:
                agents.append(agent_info)
        
        return agents
    
    async def update_agent_status(self, agent_id: str, status: str) -> bool:
        """
        Update agent status.
        
        Args:
            agent_id: ID of the agent to update
            status: New status (e.g., "idle", "busy", "offline")
            
        Returns: True if update successful, False otherwise
        """
        agent_info = await self.get_agent(agent_id)
        if not agent_info:
            return False
        
        agent_info["status"] = status
        await self.redis.set(f"agent:{agent_id}", json.dumps(agent_info))
        
        return True