#!/usr/bin/env python3
import asyncio
import json
import sys
from src.agents.kb_reconnaissance_agent import KBReconnaissanceAgent
from src.knowledge_base.importers.security_data_importer import SecurityDataImporter
from src.knowledge_base.security_kb import SecurityKnowledgeBase


async def test_kb_integration():
    """
    Test the integration between agents and the knowledge base.

    This test:
    1. Initializes the knowledge base with sample data
    2. Creates a KB-enhanced reconnaissance agent
    3. Simulates processing a task
    4. Verifies that the results include enriched information
    """
    # Initialize knowledge base
    print("Initializing security knowledge base...")
    kb = SecurityKnowledgeBase()
    importer = SecurityDataImporter(kb)
    import_results = importer.import_all_data()
    print(f"Imported {import_results['total']} items into knowledge base")

    # Create KB-enhanced reconnaissance agent
    print("\nCreating KB-enhanced reconnaissance agent...")
    agent = KBReconnaissanceAgent(agent_id="test_recon_agent")

    # Create a simulated task
    task = {
        "id": "test_task_001",
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

    # Process the task
    print("\nProcessing simulated reconnaissance task...")
    result = await agent.process_task(task)

    # Verify the results include enriched information
    if result and "services" in result:
        print("\nTask completed successfully!")
        print(f"Found {len(result['services'])} services")

        enriched_count = 0
        for service in result["services"]:
            if "enriched_info" in service and service["enriched_info"].get("potential_vulnerabilities"):
                enriched_count += 1

        print(f"Successfully enriched {enriched_count} services with knowledge base information")

        # Print a summary of the findings
        print("\nSummary:")
        print(result["summary"])

        # Print detailed information about one service as an example
        if result["services"]:
            print("\nExample enriched service information:")
            example_service = result["services"][0]
            print(
                f"Service: {example_service['service']} {example_service['version']} on port {example_service['port']}")

            if "enriched_info" in example_service and "potential_vulnerabilities" in example_service["enriched_info"]:
                vulns = example_service["enriched_info"]["potential_vulnerabilities"]
                print(f"Potential vulnerabilities: {len(vulns)}")
                for vuln in vulns:
                    print(f"- {vuln['name']} (CVE: {vuln['cve_id']}, CVSS: {vuln['cvss_score']})")

        return True
    else:
        print("Task did not complete successfully or did not return service information")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_kb_integration())
    sys.exit(0 if success else 1)