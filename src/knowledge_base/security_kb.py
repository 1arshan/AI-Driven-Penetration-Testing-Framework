from typing import Dict, List, Optional, Any
from src.knowledge_base.base_kb import BaseKnowledgeBase

class SecurityKnowledgeBase(BaseKnowledgeBase):
    """
    Security-specific knowledge base implementation.
    
    Extends the base knowledge base with collections and methods specifically
    for security patterns, vulnerabilities, and fingerprints.
    """
    
    def __init__(self):
        """
        Initialize security knowledge base with specialized collections.
        """
        super().__init__()
        
        # Define collections
        self.collections = {
            "attack_patterns": "security_attack_patterns",
            "vulnerabilities": "security_vulnerabilities",
            "exploits": "security_exploits",
            "mitigations": "security_mitigations",
            "service_fingerprints": "security_service_fingerprints"
        }
        
        # Initialize collections
        for collection in self.collections.values():
            self.create_collection(collection)
    
    def add_attack_pattern(
        self,
        pattern_id: str,
        name: str,
        description: str,
        mitre_id: Optional[str] = None,
        tactics: Optional[List[str]] = None,
        techniques: Optional[List[str]] = None
    ):
        """
        Add attack pattern to knowledge base.
        
        Args:
            pattern_id: Unique identifier for the pattern
            name: Short name of the attack pattern
            description: Detailed description of the pattern
            mitre_id: Optional MITRE ATT&CK ID (e.g., T1110.003)
            tactics: List of tactics this pattern belongs to
            techniques: List of techniques this pattern implements
            
        Returns: True if successful
        """
        metadata = {
            "pattern_id": pattern_id,
            "name": name,
            "mitre_id": mitre_id,
            "tactics": tactics or [],
            "techniques": techniques or []
        }
        
        self.add_texts(
            collection_name=self.collections["attack_patterns"],
            texts=[description],
            metadatas=[metadata],
            ids=[pattern_id]
        )
        
        return True
    
    def add_vulnerability(
        self,
        vuln_id: str,
        name: str,
        description: str,
        cve_id: Optional[str] = None,
        cvss_score: Optional[float] = None,
        affected_services: Optional[List[str]] = None,
        attack_vectors: Optional[List[str]] = None
    ):
        """
        Add vulnerability to knowledge base.
        
        Args:
            vuln_id: Unique identifier for the vulnerability
            name: Short name/title of the vulnerability
            description: Detailed description of the vulnerability
            cve_id: Optional CVE identifier
            cvss_score: Optional CVSS score (0.0-10.0)
            affected_services: List of affected service names
            attack_vectors: List of attack vector types
            
        Returns: True if successful
        """
        metadata = {
            "vuln_id": vuln_id,
            "name": name,
            "cve_id": cve_id,
            "cvss_score": cvss_score,
            "affected_services": affected_services or [],
            "attack_vectors": attack_vectors or []
        }
        
        self.add_texts(
            collection_name=self.collections["vulnerabilities"],
            texts=[description],
            metadatas=[metadata],
            ids=[vuln_id]
        )
        
        return True
    
    def add_service_fingerprint(
        self,
        fingerprint_id: str,
        service_name: str,
        version_pattern: str,
        description: str,
        default_ports: Optional[List[int]] = None,
        banner_patterns: Optional[List[str]] = None
    ):
        """
        Add service fingerprint to knowledge base.
        
        Args:
            fingerprint_id: Unique identifier for the fingerprint
            service_name: Name of the service
            version_pattern: Regex pattern to match version strings
            description: Description of the service
            default_ports: List of default ports this service runs on
            banner_patterns: List of patterns found in service banners
            
        Returns: True if successful
        """
        metadata = {
            "fingerprint_id": fingerprint_id,
            "service_name": service_name,
            "version_pattern": version_pattern,
            "default_ports": default_ports or [],
            "banner_patterns": banner_patterns or []
        }
        
        self.add_texts(
            collection_name=self.collections["service_fingerprints"],
            texts=[description],
            metadatas=[metadata],
            ids=[fingerprint_id]
        )
        
        return True
    
    def query_attack_patterns(
        self, 
        query_text: str, 
        n_results: int = 5,
        tactics: Optional[List[str]] = None
    ):
        """
        Query attack patterns by similarity and optional filters.
        
        Args:
            query_text: Text to search for
            n_results: Maximum number of results to return
            tactics: Optional list of tactics to filter by
            
        Returns: Dictionary with query results
        """
        where = None
        if tactics:
            # This is a simplified approach - actual implementation would need
            # to handle array containment queries based on ChromaDB capabilities
            where = {"tactics": {"$in": tactics}}
        
        return self.query_texts(
            collection_name=self.collections["attack_patterns"],
            query_text=query_text,
            n_results=n_results,
            where=where
        )
    
    def query_vulnerabilities(
        self,
        query_text: str,
        n_results: int = 5,
        affected_service: Optional[str] = None,
        min_cvss: Optional[float] = None
    ):
        """
        Query vulnerabilities by similarity and optional filters.
        
        Args:
            query_text: Text to search for
            n_results: Maximum number of results to return
            affected_service: Optional service name to filter by
            min_cvss: Optional minimum CVSS score to filter by
            
        Returns: Dictionary with query results
        """
        where = {}
        if affected_service:
            where["affected_services"] = {"$in": [affected_service]}
        if min_cvss is not None:
            where["cvss_score"] = {"$gte": min_cvss}
        
        return self.query_texts(
            collection_name=self.collections["vulnerabilities"],
            query_text=query_text,
            n_results=n_results,
            where=where if where else None
        )
    
    def query_service_fingerprints(
        self,
        query_text: str,
        n_results: int = 5,
        service_name: Optional[str] = None,
        port: Optional[int] = None
    ):
        """
        Query service fingerprints by similarity and optional filters.
        
        Args:
            query_text: Text to search for
            n_results: Maximum number of results to return
            service_name: Optional service name to filter by
            port: Optional port number to filter by
            
        Returns: Dictionary with query results
        """
        where = {}
        if service_name:
            where["service_name"] = service_name
        if port:
            where["default_ports"] = {"$in": [port]}
        
        return self.query_texts(
            collection_name=self.collections["service_fingerprints"],
            query_text=query_text,
            n_results=n_results,
            where=where if where else None
        )