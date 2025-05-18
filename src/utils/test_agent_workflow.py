#!/usr/bin/env python3
import asyncio
import aiohttp
import json
import uuid
from typing import Dict, Any

class AgentWorkflowTester:
    """
    Test utility for the agent workflow.
    
    This class creates a task, waits for its completion, and retrieves the results,
    demonstrating the end-to-end flow of the agent system.
    """
    
    def __init__(self, host="localhost", port=8000, token="dev_token"):
        """
        Initialize the tester.
        
        Args:
            host: Host where the MCP server is running
            port: Port of the MCP server
            token: Authentication token for API calls
        """
        self.base_url = f"http://{host}:{port}"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    async def create_task(self) -> str:
        """
        Create a reconnaissance task.
        
        Returns: Task ID if successful, otherwise raises an exception
        """
        task_data = {
            "type": "reconnaissance",
            "target": "192.168.1.1",
            "scope": {
                "ip_range": "192.168.1.0/24",
                "excluded_ips": [],
                "excluded_ports": [],
                "max_depth": 2
            },
            "description": "Test reconnaissance task",
            "priority": 2
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/task/create",
                headers=self.headers,
                json=task_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    task_id = result["task_id"]
                    print(f"Created task with ID: {task_id}")
                    return task_id
                else:
                    text = await response.text()
                    raise Exception(f"Failed to create task: {response.status} - {text}")
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a task.
        
        Args:
            task_id: ID of the task to check
            
        Returns: Dictionary with task status information
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/task/{task_id}/status",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    text = await response.text()
                    raise Exception(f"Failed to get task status: {response.status} - {text}")
    
    async def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        Get the result of a completed task.
        
        Args:
            task_id: ID of the task to get results for
            
        Returns: Dictionary with task result
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/task/{task_id}",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("result", {})
                else:
                    text = await response.text()
                    raise Exception(f"Failed to get task result: {response.status} - {text}")
    
    async def wait_for_task_completion(self, task_id: str, timeout=60) -> Dict[str, Any]:
        """
        Wait for a task to complete.
        
        Polls the task status until it's completed or failed, or until timeout.
        
        Args:
            task_id: ID of the task to wait for
            timeout: Maximum seconds to wait
            
        Returns: Final task status dictionary
        """
        start_time = asyncio.get_event_loop().time()
        while True:
            status = await self.get_task_status(task_id)
            
            print(f"Task status: {status.get('status')} - Progress: {status.get('progress')}%")
            
            if status.get("status") in ["completed", "failed"]:
                return status
            
            # Check timeout
            current_time = asyncio.get_event_loop().time()
            if current_time - start_time > timeout:
                raise TimeoutError(f"Timeout waiting for task completion after {timeout} seconds")
            
            # Wait before checking again
            await asyncio.sleep(2)
    
    async def run_test(self):
        """
        Run a complete agent workflow test.
        
        Creates a task, waits for completion, and gets the results.
        """
        try:
            # Create task
            task_id = await self.create_task()
            
            # Wait for completion
            print(f"Waiting for task {task_id} to complete...")
            final_status = await self.wait_for_task_completion(task_id)
            
            # Get results
            if final_status.get("status") == "completed":
                result = await self.get_task_result(task_id)
                print("\nTask completed successfully!")
                print(f"Result summary: {result.get('summary', '')}")
                print("\nDetailed results:")
                print(json.dumps(result, indent=2))
            else:
                print(f"Task failed: {final_status.get('message', 'Unknown error')}")
        
        except Exception as e:
            print(f"Error during test: {e}")

if __name__ == "__main__":
    tester = AgentWorkflowTester()
    asyncio.run(tester.run_test())