#!/usr/bin/env python3
import asyncio
import sys
import uuid
from src.knowledge_base.security_kb import SecurityKnowledgeBase

class SecurityDataImporter:
    """
    Importer for sample security data into the knowledge base.
    
    This utility loads sample security data into the knowledge base
    for testing and demonstration purposes.
    """
    
    def __init__(self, kb: SecurityKnowledgeBase):
        """
        Initialize with a security knowledge base.
        
        Args:
            kb: Security knowledge base instance
        """
        self.kb = kb
    
    def import_attack_patterns(self):
        """
        Import sample MITRE ATT&CK patterns.
        
        Returns: Number of patterns imported
        """
        # Sample attack patterns
        patterns = [
            {
                "id": str(uuid.uuid4()),
                "name": "Password Spraying",
                "description": "Adversaries may use a single or small list of commonly used passwords against many different accounts to attempt to acquire valid credentials. Password spraying uses one password (e.g. 'Password01'), or a small list of commonly used passwords, that may match the complexity policy of the domain. Logins are attempted with that password against many different accounts on a network to avoid account lockouts that would normally occur when brute forcing a single account with many passwords.",
                "mitre_id": "T1110.003",
                "tactics": ["Credential Access"],
                "techniques": ["Brute Force"]
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Network Service Scanning",
                "description": "Adversaries may scan for common network services that enable information gathering and remote execution. Network service scanning is the process of identifying network services through various means. Scanning may include the use of tools or commands to probe for open ports, and in some cases, active vulnerability scanning that may test the response of the targeted service to malicious inputs.",
                "mitre_id": "T1046",
                "tactics": ["Discovery"],
                "techniques": ["Network Service Discovery"]
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Exploit Public-Facing Application",
                "description": "Adversaries may attempt to exploit vulnerabilities in public-facing applications to gain initial access. Public-facing applications are those that are accessible over the internet and may include websites, content management systems (CMS), web applications, and databases. The vulnerabilities may exist due to misconfiguration, outdated software, or insecure coding practices.",
                "mitre_id": "T1190",
                "tactics": ["Initial Access"],
                "techniques": ["Exploit Public-Facing Application"]
            }
        ]
        
        # Import patterns
        for pattern in patterns:
            self.kb.add_attack_pattern(
                pattern_id=pattern["id"],
                name=pattern["name"],
                description=pattern["description"],
                mitre_id=pattern["mitre_id"],
                tactics=pattern["tactics"],
                techniques=pattern["techniques"]
            )
        
        print(f"Imported {len(patterns)} attack patterns")
        return len(patterns)
    
    def import_vulnerabilities(self):
        """
        Import sample vulnerabilities.
        
        Returns: Number of vulnerabilities imported
        """
        # Sample vulnerabilities
        vulnerabilities = [
            {
                "id": str(uuid.uuid4()),
                "name": "Apache Log4j Remote Code Execution",
                "description": "Apache Log4j2 versions 2.0-beta9 through 2.15.0 (excluding security releases 2.12.2, 2.12.3, and 2.3.1) are vulnerable to a remote code execution vulnerability where an attacker who can control log messages or log message parameters can execute arbitrary code loaded from LDAP servers when message lookup substitution is enabled.",
                "cve_id": "CVE-2021-44228",
                "cvss_score": 10.0,
                "affected_services": ["Apache Log4j", "Java"],
                "attack_vectors": ["Remote Code Execution", "JNDI Injection"]
            },
            {
                "id": str(uuid.uuid4()),
                "name": "OpenSSH Pre-Auth Double Free",
                "description": "sshd in OpenSSH 8.2 through 8.7 (before 8.8) has a double free vulnerability that allows remote attackers to cause a denial of service (memory corruption and daemon crash) or possibly execute arbitrary code if the sshd process is configured to run with underprivileged privileges.",
                "cve_id": "CVE-2021-41617",
                "cvss_score": 7.5,
                "affected_services": ["OpenSSH"],
                "attack_vectors": ["Double Free", "Memory Corruption"]
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Nginx HTTPS Request Smuggling",
                "description": "Nginx before 1.20.1 allows HTTP request smuggling because the Transfer-Encoding: chunked mechanism is improperly implemented. This issue can lead to cache poisoning, credential hijacking, or security bypass when an Nginx server is used in front of another HTTP server.",
                "cve_id": "CVE-2021-23017",
                "cvss_score": 8.6,
                "affected_services": ["Nginx"],
                "attack_vectors": ["HTTP Request Smuggling", "Cache Poisoning"]
            }
        ]
        
        # Import vulnerabilities
        for vuln in vulnerabilities:
            self.kb.add_vulnerability(
                vuln_id=vuln["id"],
                name=vuln["name"],
                description=vuln["description"],
                cve_id=vuln["cve_id"],
                cvss_score=vuln["cvss_score"],
                affected_services=vuln["affected_services"],
                attack_vectors=vuln["attack_vectors"]
            )
        
        print(f"Imported {len(vulnerabilities)} vulnerabilities")
        return len(vulnerabilities)
    
    def import_service_fingerprints(self):
        """
        Import sample service fingerprints.
        
        Returns: Number of service fingerprints imported
        """
        # Sample service fingerprints
        fingerprints = [
            {
                "id": str(uuid.uuid4()),
                "service_name": "OpenSSH",
                "version_pattern": "OpenSSH_([\\d.]+)",
                "description": "OpenSSH is the premier connectivity tool for remote login with the SSH protocol. It encrypts all traffic to eliminate eavesdropping, connection hijacking, and other attacks. In addition, OpenSSH provides a large suite of secure tunneling capabilities, several authentication methods, and sophisticated configuration options.",
                "default_ports": [22],
                "banner_patterns": ["SSH-2.0-OpenSSH"]
            },
            {
                "id": str(uuid.uuid4()),
                "service_name": "Apache HTTP Server",
                "version_pattern": "Apache/(\\d+\\.\\d+\\.\\d+)",
                "description": "The Apache HTTP Server is a powerful, flexible, HTTP/1.1 compliant web server. Apache implements the latest protocols, including HTTP/1.1 (RFC2616). It is highly configurable and extensible with third-party modules. Apache provides full source code and comes with an unrestrictive license.",
                "default_ports": [80, 443],
                "banner_patterns": ["Server: Apache"]
            },
            {
                "id": str(uuid.uuid4()),
                "service_name": "Nginx",
                "version_pattern": "nginx/(\\d+\\.\\d+\\.\\d+)",
                "description": "Nginx is a web server that can also be used as a reverse proxy, load balancer, mail proxy and HTTP cache. The software was created by Igor Sysoev and first publicly released in 2004. Nginx is known for its high performance, stability, rich feature set, simple configuration, and low resource consumption.",
                "default_ports": [80, 443],
                "banner_patterns": ["Server: nginx"]
            }
        ]
        
        # Import service fingerprints
        for fingerprint in fingerprints:
            self.kb.add_service_fingerprint(
                fingerprint_id=fingerprint["id"],
                service_name=fingerprint["service_name"],
                version_pattern=fingerprint["version_pattern"],
                description=fingerprint["description"],
                default_ports=fingerprint["default_ports"],
                banner_patterns=fingerprint["banner_patterns"]
            )
        
        print(f"Imported {len(fingerprints)} service fingerprints")
        return len(fingerprints)
    
    def import_all_data(self):
        """
        Import all sample data.
        
        Returns: Dictionary with counts of imported items
        """
        attack_count = self.import_attack_patterns()
        vuln_count = self.import_vulnerabilities()
        service_count = self.import_service_fingerprints()
        
        return {
            "attack_patterns": attack_count,
            "vulnerabilities": vuln_count,
            "service_fingerprints": service_count,
            "total": attack_count + vuln_count + service_count
        }

async def run_importer():
    """
    Run the security data importer.
    """
    print("Initializing security knowledge base...")
    kb = SecurityKnowledgeBase()
    
    print("Starting data import...")
    importer = SecurityDataImporter(kb)
    results = importer.import_all_data()
    
    print("\nImport completed:")
    print(f"- {results['attack_patterns']} attack patterns")
    print(f"- {results['vulnerabilities']} vulnerabilities")
    print(f"- {results['service_fingerprints']} service fingerprints")
    print(f"- {results['total']} total items imported")

if __name__ == "__main__":
    asyncio.run(run_importer())