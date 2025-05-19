import json
from typing import Dict, Any
from datetime import datetime


class ReportGenerator:
    """
    Generator for security assessment reports.

    This class creates formatted reports from workflow results.
    """

    @staticmethod
    def generate_html_report(workflow_results: Dict[str, Any]) -> str:
        """
        Generate an HTML security assessment report.

        Args:
            workflow_results: Results from a completed workflow

        Returns: HTML report content
        """
        # Extract key information
        target = workflow_results.get("target", "Unknown target")
        workflow_id = workflow_results.get("workflow_id", "Unknown workflow")
        created_at = workflow_results.get("created_at", datetime.now().isoformat())
        tasks = workflow_results.get("tasks", [])

        # Find the vulnerability task result
        vuln_task = next((t for t in tasks if t.get("task_type") == "vulnerability_discovery"), None)
        vuln_result = vuln_task.get("result", {}) if vuln_task else {}

        # Find the reconnaissance task result
        recon_task = next((t for t in tasks if t.get("task_type") == "reconnaissance"), None)
        recon_result = recon_task.get("result", {}) if recon_task else {}

        # Extract vulnerability data
        vuln_findings = vuln_result.get("vulnerability_findings", [])
        total_vulns = vuln_result.get("total_vulnerabilities", 0)
        critical_vulns = vuln_result.get("critical_vulnerabilities", 0)
        high_vulns = vuln_result.get("high_risk_vulnerabilities", 0)
        summary = vuln_result.get("summary", "No summary available.")

        # Create HTML content
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Security Assessment Report: {target}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                }}
                header {{
                    background: #f5f5f5;
                    padding: 20px;
                    border-bottom: 1px solid #ddd;
                    margin-bottom: 20px;
                }}
                h1, h2, h3, h4 {{
                    color: #2c3e50;
                }}
                .summary {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-left: 4px solid #4a6fa5;
                    margin-bottom: 20px;
                }}
                .statistics {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 20px;
                    flex-wrap: wrap;
                }}
                .stat-box {{
                    flex: 1;
                    min-width: 200px;
                    background: #fff;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 15px;
                    margin: 0 10px 10px 0;
                    text-align: center;
                }}
                .stat-box.critical {{
                    border-left: 4px solid #e74c3c;
                }}
                .stat-box.high {{
                    border-left: 4px solid #f39c12;
                }}
                .stat-box.medium {{
                    border-left: 4px solid #3498db;
                }}
                .stat-box.low {{
                    border-left: 4px solid #2ecc71;
                }}
                .stat-value {{
                    font-size: 2em;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th, td {{
                    padding: 12px 15px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #f5f5f5;
                }}
                tr:hover {{
                    background-color: #f9f9f9;
                }}
                .risk-level {{
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 4px;
                    color: white;
                    font-weight: bold;
                }}
                .risk-critical {{
                    background-color: #e74c3c;
                }}
                .risk-high {{
                    background-color: #f39c12;
                }}
                .risk-medium {{
                    background-color: #3498db;
                }}
                .risk-low {{
                    background-color: #2ecc71;
                }}
                footer {{
                    margin-top: 30px;
                    padding: 20px;
                    text-align: center;
                    background: #f5f5f5;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>Security Assessment Report</h1>
                    <p>Target: <strong>{target}</strong></p>
                    <p>Report Date: <strong>{datetime.now().strftime('%Y-%m-%d')}</strong></p>
                    <p>Assessment ID: <strong>{workflow_id}</strong></p>
                </header>

                <section>
                    <h2>Executive Summary</h2>
                    <div class="summary">
                        <p>{summary}</p>
                    </div>

                    <div class="statistics">
                        <div class="stat-box critical">
                            <h3>Critical</h3>
                            <div class="stat-value">{critical_vulns}</div>
                            <p>Vulnerabilities</p>
                        </div>
                        <div class="stat-box high">
                            <h3>High</h3>
                            <div class="stat-value">{high_vulns}</div>
                            <p>Vulnerabilities</p>
                        </div>
                        <div class="stat-box medium">
                            <h3>Total</h3>
                            <div class="stat-value">{total_vulns}</div>
                            <p>Vulnerabilities</p>
                        </div>
                        <div class="stat-box low">
                            <h3>Services</h3>
                            <div class="stat-value">{len(vuln_findings)}</div>
                            <p>Analyzed</p>
                        </div>
                    </div>
                </section>

                <section>
                    <h2>Vulnerability Findings</h2>
        """

        # Add each service and its vulnerabilities
        for service in vuln_findings:
            service_name = service.get("service", "Unknown service")
            version = service.get("version", "Unknown version")
            port = service.get("port", "Unknown port")

            html += f"""
                    <h3>{service_name} {version} (Port {port})</h3>
                    <p>Found {service.get('total_vulnerabilities', 0)} vulnerabilities.</p>

                    <table>
                        <thead>
                            <tr>
                                <th>Vulnerability</th>
                                <th>CVE ID</th>
                                <th>Risk Level</th>
                                <th>CVSS Score</th>
                            </tr>
                        </thead>
                        <tbody>
            """

            # Add rows for each vulnerability
            for vuln in service.get("vulnerabilities", []):
                name = vuln.get("name", "Unknown vulnerability")
                cve_id = vuln.get("cve_id", "No CVE")
                risk_level = vuln.get("risk_level", "Low")
                cvss_score = vuln.get("cvss_score", 0.0)

                risk_class = f"risk-{risk_level.lower()}"

                html += f"""
                            <tr>
                                <td>{name}</td>
                                <td>{cve_id}</td>
                                <td><span class="risk-level {risk_class}">{risk_level}</span></td>
                                <td>{cvss_score}</td>
                            </tr>
                """

            html += """
                        </tbody>
                    </table>
            """

        # Complete the HTML document
        html += f"""
                </section>

                <footer>
                    <p>Generated by AI-Driven Penetration Testing Framework</p>
                    <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </footer>
            </div>
        </body>
        </html>
        """

        return html