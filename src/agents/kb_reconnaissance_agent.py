import asyncio
import json
from typing import Dict, List, Any
from src.agents.base_agent import BaseAgent
from src.knowledge_base.security_kb import SecurityKnowledgeBase


class KBReconnaissanceAgent(BaseAgent):
    """
    Enhanced reconnaissance agent that leverages the knowledge base.

    This agent extends the basic reconnaissance functionality by using
    the security knowledge base to enrich its findings with context
    and potential vulnerabilities.
    """

    def __init__(self, agent_id=None):
        """
        Initialize a knowledge-enhanced reconnaissance agent.

        Args:
            agent_id: Optional unique ID for the agent
        """
        super().__init__(agent_type="reconnaissance", agent_id=agent_id)
        self.kb = SecurityKnowledgeBase()

    def get_capabilities(self) -> List[str]:
        """
        Get the capabilities of this reconnaissance agent.

        Returns: List of capability strings
        """
        return [
            "network_scanning",
            "port_discovery",
            "service_detection",
            "os_fingerprinting",
            "banner_grabbing",
            "vulnerability_assessment"
        ]

    async def enrich_service_info(self, service_name: str, version: str, port: int) -> Dict[str, Any]:
        """
        Enrich service information with data from the knowledge base.

        Args:
            service_name: Name of the detected service
            version: Version string of the service
            port: Port number the service is running on

        Returns: Dictionary with enriched service information
        """
        # Query service fingerprints
        fingerprint_results = self.kb.query_service_fingerprints(
            query_text=f"{service_name} {version}",
            n_results=1,
            service_name=service_name
        )

        # Query potential vulnerabilities
        vulnerability_results = self.kb.query_vulnerabilities(
            query_text=f"{service_name} {version} vulnerability",
            n_results=3,
            affected_service=service_name
        )

        # Extract relevant information
        service_info = {}

        # Get service details
        if fingerprint_results and fingerprint_results.get("documents") and len(
                fingerprint_results["documents"][0]) > 0:
            service_info["description"] = fingerprint_results["documents"][0][0]
            if fingerprint_results.get("metadatas") and len(fingerprint_results["metadatas"][0]) > 0:
                service_info["metadata"] = fingerprint_results["metadatas"][0][0]

        # Get potential vulnerabilities
        potential_vulns = []
        if vulnerability_results and vulnerability_results.get("documents") and len(
                vulnerability_results["documents"][0]) > 0:
            for i, doc in enumerate(vulnerability_results["documents"][0]):
                if i < len(vulnerability_results["metadatas"][0]):
                    vuln_metadata = vulnerability_results["metadatas"][0][i]
                    potential_vulns.append({
                        "name": vuln_metadata.get("name", "Unknown vulnerability"),
                        "cve_id": vuln_metadata.get("cve_id", "Unknown"),
                        "cvss_score": vuln_metadata.get("cvss_score", 0.0),
                        "description": doc[:200] + "..." if len(doc) > 200 else doc
                    })

        service_info["potential_vulnerabilities"] = potential_vulns

        return service_info

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a reconnaissance task with knowledge base integration.

        This implementation simulates reconnaissance and enriches the
        findings with data from the security knowledge base.

        Args:
            task: Dictionary containing the task details

        Returns: Dictionary containing the enriched reconnaissance results
        """
        target = task.get("target")
        scope = task.get("scope", {})
        task_id = task.get("id")

        # Log the start of processing
        print(f"Starting reconnaissance on target: {target}")
        await self.update_task_status(
            task_id=task_id,
            status="in_progress",
            progress=10.0,
            message=f"Starting reconnaissance on {target}"
        )

        # Simulate network scanning
        await asyncio.sleep(2)  # Simulate time taken by the scan
        await self.update_task_status(
            task_id=task_id,
            status="in_progress",
            progress=30.0,
            message="Network scanning in progress"
        )

        # Simulate finding open ports and services
        discovered_services = [
            {"port": 22, "service": "OpenSSH", "version": "8.2p1", "banner": "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5"},
            {"port": 80, "service": "Apache HTTP Server", "version": "2.4.41",
             "banner": "Server: Apache/2.4.41 (Ubuntu)"},
            {"port": 443, "service": "Nginx", "version": "1.18.0", "banner": "Server: nginx/1.18.0 (Ubuntu)"}
        ]

        await asyncio.sleep(2)
        await self.update_task_status(
            task_id=task_id,
            status="in_progress",
            progress=50.0,
            message=f"Found {len(discovered_services)} services, enriching with knowledge base"
        )

        # Enrich service information with knowledge base
        enriched_services = []
        for i, service in enumerate(discovered_services):
            await self.update_task_status(
                task_id=task_id,
                status="in_progress",
                progress=50.0 + (i + 1) * 10.0,
                message=f"Enriching information for {service['service']} on port {service['port']}"
            )

            enriched_info = await self.enrich_service_info(
                service_name=service["service"],
                version=service["version"],
                port=service["port"]
            )

            enriched_services.append({
                **service,
                "enriched_info": enriched_info
            })

        # Simulate OS fingerprinting
        os_info = "Linux Ubuntu 20.04"
        await asyncio.sleep(1)
        await self.update_task_status(
            task_id=task_id,
            status="in_progress",
            progress=90.0,
            message="OS fingerprinting completed"
        )

        # Generate reconnaissance summary using Claude
        summary_prompt = f"""
        Create a concise summary of the reconnaissance findings, including potential vulnerabilities:

        Target: {target}
        Operating System: {os_info}

        Discovered Services:
        {json.dumps([{
            "port": s["port"],
            "service": s["service"],
            "version": s["version"],
            "potential_vulnerabilities": [v["name"] for v in s["enriched_info"]["potential_vulnerabilities"]]
        } for s in enriched_services], indent=2)}

        Please provide a brief, professional summary of these findings, highlighting the most critical vulnerabilities based on CVSS scores.
        """

        summary = await self.claude.generate_response(
            system_prompt="You are a security professional summarizing reconnaissance findings.",
            user_message=summary_prompt
        )

        # Compile results
        result = {
            "target": target,
            "os_info": os_info,
            "services": enriched_services,
            "summary": summary
        }

        return result