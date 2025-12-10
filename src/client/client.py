"""
AI-Ops API Client for posting insights to the platform endpoint.

This module contains the client functionality for making API requests
to the AI-Ops platform.
"""

import os
import requests
from typing import Dict
from dotenv import load_dotenv


class AIOpsClient:
    def __init__(self, endpoint: str = None, token: str = None, dry_run: bool = False):
        # Load environment variables
        load_dotenv()
        
        # Use provided endpoint or get from env, fallback to default
        if endpoint:
            self.endpoint = endpoint
        else:
            base_url = os.getenv('AIOPS_BASE_URL', 'http://localhost:4047')
            self.endpoint = f"{base_url}/api/platform/ai-ops-insights/v1/insights"
        
        # Use provided token or get from env
        self.token = token or os.getenv('AIOPS_TOKEN')
        self.dry_run = dry_run
    
    def post_insight(self, insight: Dict, window_info: str = None) -> bool:
        """Post an insight to the AI-Ops API endpoint."""
        uid = insight.get('uid', 'Unknown')
        title = insight.get('title', 'Unknown')
        
        if self.dry_run:
            log_msg = f"[DRY RUN] Would post insight"
            if window_info:
                log_msg += f" [{window_info}]"
            log_msg += f": {title} (UID: {uid})"
            print(log_msg)
            if self.token:
                print(f"[DRY RUN] Would use Bearer token: {self.token[:10]}...")
            return True
            
        try:
            headers = {"Content-Type": "application/json"}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            response = requests.post(
                self.endpoint,
                json=insight,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200 or response.status_code == 201:
                log_msg = f"✓ Successfully posted insight"
                if window_info:
                    log_msg += f" [{window_info}]"
                log_msg += f": {title} (UID: {uid})"
                print(log_msg)
                return True
            else:
                log_msg = f"✗ Failed to post insight"
                if window_info:
                    log_msg += f" [{window_info}]"
                log_msg += f": {title} (UID: {uid}) - {response.status_code} - {response.text}"
                print(log_msg)
                return False
                
        except requests.exceptions.RequestException as e:
            log_msg = f"✗ Error posting insight"
            if window_info:
                log_msg += f" [{window_info}]"
            log_msg += f": {title} (UID: {uid}) - {e}"
            print(log_msg)
            return False
    
    def clear_all_insights(self) -> bool:
        """Clear all insights from the AI-Ops API endpoint using DELETE method."""
        if self.dry_run:
            print("[DRY RUN] Would delete all insights from the platform")
            if self.token:
                print(f"[DRY RUN] Would use Bearer token: {self.token[:10]}...")
            return True
            
        try:
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            print(f"Sending DELETE request to: {self.endpoint}")
            response = requests.delete(
                self.endpoint,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 204, 404]:  # 404 acceptable if no insights exist
                return True
            else:
                print(f"✗ Failed to clear insights - {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Error clearing insights: {e}")
            return False
    
    def get_endpoint(self) -> str:
        """Get the configured endpoint URL."""
        return self.endpoint
    
    def has_token(self) -> bool:
        """Check if authentication token is configured."""
        return bool(self.token)
    
    def get_token_preview(self) -> str:
        """Get a preview of the configured token (first 10 characters)."""
        if self.token:
            return f"{self.token[:10]}..."
        return "None"