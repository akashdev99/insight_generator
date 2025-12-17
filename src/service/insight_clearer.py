"""
Insight Clearer Service

This module handles the clearing/deletion of all insights from a platform.
"""

from ..client import AIOpsClient


class InsightClearer:
    def __init__(self, endpoint: str = None, token: str = None, dry_run: bool = False):
        """Initialize the insight clearer with optional endpoint and token."""
        self.endpoint = endpoint
        self.token = token
        self.dry_run = dry_run
    
    def clear_with_confirmation(self) -> bool:
        """
        Clear all insights from the platform with user confirmation.
        
        Returns:
            bool: True if clearing was successful, False otherwise
        """
        print("⚠️  WARNING: This will delete ALL insights from the platform!")
        confirmation = input("Are you sure you want to continue? (yes/no): ").lower().strip()
        
        if confirmation == 'yes':
            return self.clear_insights()
        else:
            print("Operation cancelled.")
            return False
    
    def clear_insights(self) -> bool:
        """
        Clear all insights from the platform without confirmation.
        
        Returns:
            bool: True if clearing was successful, False otherwise
        """
        client = AIOpsClient(self.endpoint, self.token, self.dry_run)
        return client.clear_all_insights()