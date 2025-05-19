import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import redis.asyncio as redis
from src.utils.config import Config


class WorkflowOrchestrator:
    """
    Orchestrator for multi-agent workflows.

    This class handles the coordination of tasks between multiple agents
    to complete security testing workflows.
    """

    def __init__(self):
        """
        Initialize the workflow orchestrator with Redis connection.
        """
        self.redis = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB
        )

    async def create_workflow(self, workflow_type: str, target: str, scope: Dict[str, Any]) -> str:
        """
        Create a new workflow.

        Args:
            workflow_type: Type of workflow (e.g., "recon_vuln")
            target: Target of the workflow
            scope: Dictionary containing scope information

        Returns: Workflow ID
        """
        workflow_id = str(uuid.uuid4())

        workflow_data = {
            "id": workflow_id,
            "type": workflow_type,
            "target": target,
            "scope": scope,
            "status": "created",
            "tasks": [],
            "created_at": datetime.now().isoformat()
        }

        # Store workflow data
        await self.redis.set(f"workflow:{workflow_id}", json.dumps(workflow_data))

        return workflow_id

    async def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow data by ID.

        Args:
            workflow_id: ID of the workflow

        Returns: Workflow data dictionary if found, None otherwise
        """
        workflow_data = await self.redis.get(f"workflow:{workflow_id}")
        if workflow_data:
            return json.loads(workflow_data)
        return None

    async def update_workflow_status(self, workflow_id: str, status: str) -> bool:
        """
        Update workflow status.

        Args:
            workflow_id: ID of the workflow
            status: New status

        Returns: True if successful, False otherwise
        """
        workflow_data = await self.get_workflow(workflow_id)
        if not workflow_data:
            return False

        workflow_data["status"] = status
        workflow_data["updated_at"] = datetime.now().isoformat()

        await self.redis.set(f"workflow:{workflow_id}", json.dumps(workflow_data))
        return True

    async def add_task_to_workflow(self, workflow_id: str, task_id: str, task_type: str) -> bool:
        """
        Add a task to a workflow.

        Args:
            workflow_id: ID of the workflow
            task_id: ID of the task
            task_type: Type of the task

        Returns: True if successful, False otherwise
        """
        workflow_data = await self.get_workflow(workflow_id)
        if not workflow_data:
            return False

        workflow_data["tasks"].append({
            "task_id": task_id,
            "task_type": task_type,
            "added_at": datetime.now().isoformat()
        })

        await self.redis.set(f"workflow:{workflow_id}", json.dumps(workflow_data))
        return True

    async def start_recon_vuln_workflow(self, target: str, scope: Dict[str, Any], description: str) -> str:
        """
        Start a reconnaissance and vulnerability discovery workflow.

        This workflow consists of:
        1. Reconnaissance task
        2. Vulnerability discovery task that depends on the recon results

        Args:
            target: Target system to test
            scope: Dictionary containing scope information
            description: Description of the workflow

        Returns: Workflow ID
        """
        # Create workflow
        workflow_id = await self.create_workflow("recon_vuln", target, scope)

        # Create reconnaissance task
        recon_task_data = {
            "type": "reconnaissance",
            "target": target,
            "scope": scope,
            "description": f"Reconnaissance for {description}",
            "priority": 2,
            "workflow_id": workflow_id
        }

        # Convert to JSON and store in Redis
        recon_task_id = str(uuid.uuid4())
        recon_task_data["id"] = recon_task_id
        recon_task_data["status"] = "created"
        recon_task_data["created_at"] = datetime.now().isoformat()

        await self.redis.set(f"task:{recon_task_id}", json.dumps(recon_task_data))

        # Add to queue
        await self.redis.lpush(f"queue:reconnaissance", recon_task_id)

        # Add to workflow
        await self.add_task_to_workflow(workflow_id, recon_task_id, "reconnaissance")

        # Update workflow status
        await self.update_workflow_status(workflow_id, "in_progress")

        # Set up task completion handler (Redis subscription)
        asyncio.create_task(self._monitor_recon_completion(workflow_id, recon_task_id, target, scope))

        return workflow_id

    async def _monitor_recon_completion(self, workflow_id: str, recon_task_id: str, target: str, scope: Dict[str, Any]):
        """
        Monitor reconnaissance task completion and start vulnerability discovery.

        Args:
            workflow_id: ID of the workflow
            recon_task_id: ID of the reconnaissance task
            target: Target system
            scope: Dictionary containing scope information
        """
        # Set up Redis pubsub
        pubsub = self.redis.pubsub()
        await pubsub.subscribe("task_updates")

        while True:
            try:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message and message["type"] == "message":
                    data = json.loads(message["data"].decode("utf-8"))

                    # Check if this is a completion message for our task
                    if (data.get("event") == "task_completed" and
                            data.get("task_id") == recon_task_id):
                        print(f"Reconnaissance task {recon_task_id} completed, starting vulnerability discovery")

                        # Get recon results
                        recon_result_data = await self.redis.get(f"result:{recon_task_id}")
                        if not recon_result_data:
                            print(f"Error: No results found for recon task {recon_task_id}")
                            await pubsub.unsubscribe("task_updates")
                            return

                        recon_result = json.loads(recon_result_data)

                        # Create vulnerability discovery task
                        vuln_task_data = {
                            "type": "vulnerability_discovery",
                            "target": target,
                            "scope": scope,
                            "description": f"Vulnerability discovery for {target}",
                            "priority": 2,
                            "workflow_id": workflow_id,
                            "parent_task_id": recon_task_id
                        }

                        # Convert to JSON and store in Redis
                        vuln_task_id = str(uuid.uuid4())
                        vuln_task_data["id"] = vuln_task_id
                        vuln_task_data["status"] = "created"
                        vuln_task_data["created_at"] = datetime.now().isoformat()

                        await self.redis.set(f"task:{vuln_task_id}", json.dumps(vuln_task_data))

                        # Add to queue
                        await self.redis.lpush(f"queue:vulnerability_discovery", vuln_task_id)

                        # Add to workflow
                        await self.add_task_to_workflow(workflow_id, vuln_task_id, "vulnerability_discovery")

                        # Set up task completion handler
                        asyncio.create_task(self._monitor_vuln_completion(workflow_id, vuln_task_id))

                        # Unsubscribe since we've handled this task
                        await pubsub.unsubscribe("task_updates")
                        return

                # Small delay to prevent CPU overuse
                await asyncio.sleep(0.01)
            except Exception as e:
                print(f"Error monitoring recon completion: {e}")
                await asyncio.sleep(1)

    async def _monitor_vuln_completion(self, workflow_id: str, vuln_task_id: str):
        """
        Monitor vulnerability discovery task completion and finalize workflow.

        Args:
            workflow_id: ID of the workflow
            vuln_task_id: ID of the vulnerability discovery task
        """
        # Set up Redis pubsub
        pubsub = self.redis.pubsub()
        await pubsub.subscribe("task_updates")

        while True:
            try:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message and message["type"] == "message":
                    data = json.loads(message["data"].decode("utf-8"))

                    # Check if this is a completion message for our task
                    if (data.get("event") == "task_completed" and
                            data.get("task_id") == vuln_task_id):
                        print(f"Vulnerability discovery task {vuln_task_id} completed, workflow {workflow_id} complete")

                        # Update workflow status
                        await self.update_workflow_status(workflow_id, "completed")

                        # Unsubscribe since we've handled this task
                        await pubsub.unsubscribe("task_updates")
                        return

                # Small delay to prevent CPU overuse
                await asyncio.sleep(0.01)
            except Exception as e:
                print(f"Error monitoring vuln completion: {e}")
                await asyncio.sleep(1)

    async def get_workflow_results(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get the results of a workflow.

        Args:
            workflow_id: ID of the workflow

        Returns: Dictionary with workflow results
        """
        workflow_data = await self.get_workflow(workflow_id)
        if not workflow_data:
            return {"error": "Workflow not found"}

        # Get task results
        task_results = []
        for task in workflow_data.get("tasks", []):
            task_id = task.get("task_id")
            task_data = await self.redis.get(f"task:{task_id}")
            result_data = await self.redis.get(f"result:{task_id}")

            if task_data:
                task_info = json.loads(task_data)
                result = json.loads(result_data) if result_data else None

                task_results.append({
                    "task_id": task_id,
                    "task_type": task.get("task_type"),
                    "status": task_info.get("status"),
                    "result": result.get("result") if result else None
                })

        return {
            "workflow_id": workflow_id,
            "status": workflow_data.get("status"),
            "target": workflow_data.get("target"),
            "tasks": task_results,
            "created_at": workflow_data.get("created_at"),
            "updated_at": workflow_data.get("updated_at", workflow_data.get("created_at"))
        }