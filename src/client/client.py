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
    
    def load_and_transfer_insights(self, source_domain: str, target_domain: str) -> bool:
        """Load insights from source domain and transfer to target domain."""
        print(f"📋 Fetching insights from source domain...")
        insights = self.fetch_insights_from_domain(source_domain)
        
        if not insights:
            print("⚠️  No insights found in source domain or failed to fetch.")
            return False
        
        print(f"📦 Found {len(insights)} insights to transfer")
        
        success_count = 0
        failed_count = 0
        
        # Create a new client instance for posting to target domain
        target_client = AIOpsClient(self._build_endpoint(target_domain), self.token, self.dry_run)
        
        for i, insight in enumerate(insights, 1):
            print(f"🔄 Processing insight {i}/{len(insights)}: {insight.get('title', 'Unknown')}")
            
            if target_client.post_insight(insight, f"TENANT_LOAD: {i}/{len(insights)}"):
                success_count += 1
            else:
                failed_count += 1
        
        print(f"\\n📊 Transfer Summary:")
        print(f"   ✅ Successfully transferred: {success_count}")
        print(f"   ❌ Failed transfers: {failed_count}")
        print(f"   📈 Success rate: {(success_count/len(insights)*100):.1f}%")
        
        return failed_count == 0
    
    def fetch_insights_from_domain(self, domain: str) -> list:
        """Fetch all insights from a domain with limit of 300."""
        try:
            endpoint = self._build_endpoint(domain)
            
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            # Add query parameter for limit
            params = {"limit": 300}
            
            if self.dry_run:
                print(f"[DRY RUN] Would fetch insights from: {endpoint}")
                print(f"[DRY RUN] With parameters: {params}")
                # Return mock data for dry run
                return [
                    {"uid": "mock-1", "title": "Mock Insight 1", "severity": "CRITICAL"},
                    {"uid": "mock-2", "title": "Mock Insight 2", "severity": "WARNING"}
                ]
            
            print(f"🌐 GET {endpoint}")
            print(f"📝 Query parameters: {params}")
            
            response = requests.get(
                endpoint,
                headers=headers,
                params=params,
                timeout=60  # Longer timeout for potentially large response
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle different response formats
                if isinstance(data, list):
                    insights = data
                elif isinstance(data, dict):
                    # Try common field names for insights array
                    insights = data.get('data', data.get('insights', data.get('items', [])))
                else:
                    insights = []
                
                print(f"✅ Successfully fetched {len(insights)} insights")
                return insights
            else:
                print(f"❌ Failed to fetch insights - {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching insights: {e}")
            return []
    
    def _build_endpoint(self, domain: str) -> str:
        """Build the full API endpoint URL from domain."""
        # Remove any trailing slashes and protocol if provided
        clean_domain = domain.rstrip('/')
        if not clean_domain.startswith(('http://', 'https://')):
            clean_domain = f"https://{clean_domain}"
        
        return f"{clean_domain}/api/platform/ai-ops-insights/v1/insights"
    
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