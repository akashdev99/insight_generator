"""
Insight Migrator Service

This module handles the migration of insights from one domain to another.
"""

import os
from ..client import AIOpsClient


class InsightMigrator:
    def __init__(self, endpoint: str = None, token: str = None, dry_run: bool = False):
        """Initialize the insight migrator with optional endpoint and token."""
        self.endpoint = endpoint
        self.token = token
        self.dry_run = dry_run
    
    def migrate_insights(self, source_domain: str) -> bool:
        """
        Migrate insights from source domain to target domain.
        
        Args:
            source_domain: The domain to fetch insights from
            
        Returns:
            bool: True if migration was successful, False otherwise
        """
        target_domain = os.getenv('AIOPS_DOMAIN')
        
        if not target_domain:
            print("Error: AIOPS_DOMAIN environment variable must be set for target domain.")
            return False
        
        print(f"📥 Loading insights from: {source_domain}")
        print(f"📤 Target domain: {target_domain}")
        
        client = AIOpsClient(self.endpoint, self.token, self.dry_run)
        success = client.load_and_transfer_insights(source_domain, target_domain)
        
        return success