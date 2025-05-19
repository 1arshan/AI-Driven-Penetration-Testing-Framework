import asyncio
import json
from typing import Dict, List, Any
from src.agents.base_agent import BaseAgent
from src.knowledge_base.security_kb import SecurityKnowledgeBase


class KnowledgeBaseAgent(BaseAgent):
    """
    Agent that provides access to the security knowledge base.

    This agent handles knowledge queries from other agents and returns
    relevant information from the knowledge base.
    """

    def __init__(self, agent_id=None):
        """
        Initialize a knowledge base agent.

        Args:
            agent_id: Optional unique ID for the agent
        """
        agent_id = agent_id or "knowledge_base_agent"
        super().__init__(agent_type="knowledge_base", agent_id=agent_id)
        self.kb = SecurityKnowledgeBase()

    def get_capabilities(self) -> List[str]:
        """
        Get the capabilities of this knowledge base agent.

        Returns: List of capability strings
        """
        return [
            "knowledge_query",
            "attack_pattern_lookup",
            "vulnerability_lookup",
            "service_fingerprint_lookup"
        ]

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a knowledge base task.

        Args:
            task: Dictionary containing the task details

        Returns: Dictionary containing the task results
        """
        # Knowledge base agent doesn't typically process tasks from the queue
        # but this method is required by the BaseAgent class
        return {
            "status": "success",
            "summary": "Knowledge base agent doesn't process standard tasks"
        }

    async def initialize_messaging(self):
        """
        Initialize messaging for the knowledge base agent.

        Registers handlers for knowledge query messages.
        """
        await super().initialize_messaging()

        # Register knowledge query handler
        await self.message_bus.register_handler("knowledge_query", self.handle_knowledge_query)

    async def handle_knowledge_query(self, message: Dict[str, Any]):
        """
        Handle a knowledge query message.

        Processes the query and sends back a response with the results.

        Args:
            message: Dictionary containing the knowledge query
        """
        print(f"Knowledge base agent received query: {message.get('content', {}).get('query')}")

        query_content = message.get("content", {})
        query_text = query_content.get("query", "")
        collection = query_content.get("collection", "")
        n_results = query_content.get("n_results", 5)

        if not query_text or not collection:
            print("Invalid knowledge query: missing query or collection")
            return

        # Process query based on collection type
        results = None
        if collection == "attack_patterns":
            results = self.kb.query_attack_patterns(query_text, n_results=n_results)
        elif collection == "vulnerabilities":
            results = self.kb.query_vulnerabilities(query_text, n_results=n_results)
        elif collection == "service_fingerprints":
            results = self.kb.query_service_fingerprints(query_text, n_results=n_results)
        else:
            print(f"Unknown collection type: {collection}")
            return

        # Format results for response
        formatted_results = self._format_query_results(results)

        # Send response
        await self.send_message({
            "message_type": "knowledge_response",
            "recipient_id": message.get("sender_id"),
            "reply_to": message.get("message_id"),
            "content": {
                "query": query_text,
                "collection": collection,
                "results": formatted_results
            }
        })

    def _format_query_results(self, results):
        """
        Format ChromaDB results into a more usable structure.

        Args:
            results: Raw results from ChromaDB query

        Returns: List of formatted result dictionaries
        """
        formatted = []

        if not results or not results.get("documents") or not results.get("documents")[0]:
            return formatted

        for i, doc in enumerate(results["documents"][0]):
            result = {
                "document": doc,
                "metadata": {}
            }

            # Add metadata if available
            if results.get("metadatas") and i < len(results["metadatas"][0]):
                result["metadata"] = results["metadatas"][0][i]

            # Add distance/similarity score if available
            if results.get("distances") and i < len(results["distances"][0]):
                result["similarity"] = 1.0 - results["distances"][0][i]

            formatted.append(result)

        return formatted