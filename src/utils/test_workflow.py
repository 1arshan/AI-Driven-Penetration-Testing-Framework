#!/usr/bin/env python3
import asyncio
import aiohttp
import json
import argparse
import sys
import time


class WorkflowTester:
    """
    Test utility for multi-agent workflows.

    This class provides functionality to test the recon_vuln workflow
    that chains reconnaissance and vulnerability discovery.
    """

    def __init__(self, host="localhost", port=8000, token="dev_token"):
        """
        Initialize the workflow tester.

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

    async def create_workflow(self, target="192.168.1.1"):
        """
        Create a reconnaissance and vulnerability discovery workflow.

        Args:
            target: Target IP or hostname

        Returns: Workflow ID if successful
        """
        workflow_data = {
            "target": target,
            "scope": {
                "ip_range": "192.168.1.0/24",
                "excluded_ips": [],
                "excluded_ports": [],
                "max_depth": 2
            },
            "description": "Test security assessment"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{self.base_url}/api/workflows/recon_vuln",
                    headers=self.headers,
                    json=workflow_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    workflow_id = result.get("workflow_id")
                    print(f"Created workflow with ID: {workflow_id}")
                    return workflow_id
                else:
                    text = await response.text()
                    raise Exception(f"Failed to create workflow: {response.status} - {text}")

    async def get_workflow_status(self, workflow_id):
        """
        Get the status of a workflow.

        Args:
            workflow_id: ID of the workflow

        Returns: Workflow status data
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{self.base_url}/api/workflows/{workflow_id}",
                    headers=self.headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    text = await response.text()
                    raise Exception(f"Failed to get workflow status: {response.status} - {text}")

    async def get_workflow_results(self, workflow_id):
        """
        Get the results of a workflow.

        Args:
            workflow_id: ID of the workflow

        Returns: Workflow results
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{self.base_url}/api/workflows/{workflow_id}/results",
                    headers=self.headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    text = await response.text()
                    raise Exception(f"Failed to get workflow results: {response.status} - {text}")

    async def wait_for_workflow_completion(self, workflow_id, timeout=300, check_interval=5):
        """
        Wait for a workflow to complete.

        Args:
            workflow_id: ID of the workflow
            timeout: Maximum seconds to wait
            check_interval: Seconds between status checks

        Returns: Final workflow status
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = await self.get_workflow_status(workflow_id)

            print(f"Workflow status: {status.get('status')}")
            print(f"Tasks: {len(status.get('tasks', []))}")

            if status.get("status") == "completed":
                return status

            # Wait before checking again
            await asyncio.sleep(check_interval)

        raise TimeoutError(f"Workflow did not complete within {timeout} seconds")

    async def run_test(self, target="192.168.1.1", wait_for_completion=True):
        """
        Run a complete workflow test.

        Args:
            target: Target IP or hostname
            wait_for_completion: Whether to wait for workflow completion

        Returns: Workflow results if wait_for_completion is True
        """
        try:
            # Create workflow
            workflow_id = await self.create_workflow(target)

            # Wait for completion if requested
            if wait_for_completion:
                print(f"Waiting for workflow {workflow_id} to complete...")
                await self.wait_for_workflow_completion(workflow_id)

                # Get results
                results = await self.get_workflow_results(workflow_id)

                print("\nWorkflow completed!")
                print(f"Target: {results.get('target')}")

                # Print task results
                for task in results.get("tasks", []):
                    print(f"\nTask: {task.get('task_type')}")
                    print(f"Status: {task.get('status')}")

                    if task.get("result"):
                        result = task.get("result")
                        if "summary" in result:
                            print(f"\nSummary: {result.get('summary')}")

                        if task.get("task_type") == "vulnerability_discovery":
                            vulns = result.get("vulnerability_findings", [])
                            total_vulns = result.get("total_vulnerabilities", 0)
                            print(f"\nFound {total_vulns} vulnerabilities across {len(vulns)} services:")

                            for service in vulns:
                                print(
                                    f"\n- {service.get('service')} {service.get('version')} on port {service.get('port')}")
                                print(
                                    f"  {service.get('total_vulnerabilities')} vulnerabilities found (highest risk: {service.get('highest_risk')})")

                                # Show top vulnerabilities
                                for vuln in service.get("vulnerabilities", [])[:3]:  # Show top 3
                                    print(
                                        f"  - {vuln.get('name')} (CVE: {vuln.get('cve_id')}, CVSS: {vuln.get('cvss_score')})")

                                if len(service.get("vulnerabilities", [])) > 3:
                                    print(f"    ... and {len(service.get('vulnerabilities', [])) - 3} more")

                    return results
                else:
                    print(f"Workflow {workflow_id} started. Not waiting for completion.")
                    return {"workflow_id": workflow_id}

        except Exception as e:
            print(f"Error during workflow test: {e}")
            return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test multi-agent workflow")
    parser.add_argument("--target", default="192.168.1.1", help="Target IP or hostname")
    parser.add_argument("--no-wait", action="store_true", help="Don't wait for workflow completion")

    args = parser.parse_args()

    tester = WorkflowTester()
    asyncio.run(tester.run_test(args.target, not args.no_wait))
