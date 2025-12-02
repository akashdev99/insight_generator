"""
InsightGenerator class for AI-Ops Insights Generator CLI Tool

This module contains the core functionality for generating and posting
insights to the AI-Ops platform endpoint.
"""

import json
import os
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any
from pathlib import Path
from ..client import AIOpsClient
from ..inventory import DeviceInventory


class InsightGenerator:
    def __init__(self, config_file: str, endpoint: str = None, token: str = None, dry_run: bool = False):
        self.config_file = config_file
        self.client = AIOpsClient(endpoint, token, dry_run)
        
        # Initialize device inventory with same endpoint and token
        self.device_inventory = DeviceInventory(endpoint, token)
        
        # Round-robin counters for each insight type
        self.forecast_counter = 0
        self.current_counter = 0
        self.past_counter = 0
        
        # Available severity levels
        self.severity_levels = ["CRITICAL", "WARNING", "INFORMATIONAL"]
        
        self.base_dir = Path(config_file).parent
        self.forecast_dir = self.base_dir / "forecast"
        self.current_dir = self.base_dir / "current"
        self.past_dir = self.base_dir / "past"
        
    def load_config(self) -> Dict:
        """Load the forecast configuration JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file {self.config_file} not found.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in configuration file: {e}")
            sys.exit(1)
    
    def load_insights_from_folder(self, folder_path: Path) -> List[Dict]:
        """Load all JSON insight files from a folder."""
        insights = []
        if not folder_path.exists():
            print(f"Warning: Folder {folder_path} does not exist.")
            return insights
            
        for file_path in folder_path.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    insight = json.load(f)
                    insights.append(insight)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load insight from {file_path}: {e}")
                
        return insights
    
    def get_round_robin_insight(self, insights: List[Dict], counter_attr: str) -> Dict:
        """Get insight in round-robin fashion using the specified counter."""
        if not insights:
            return None
            
        counter = getattr(self, counter_attr)
        insight = insights[counter % len(insights)].copy()
        setattr(self, counter_attr, counter + 1)
        return insight
    
    def modify_insight_properties(self, insight: Dict) -> Dict:
        """Modify insight properties: UID, severity, and impacted device."""
        # Generate new UID
        insight["uid"] = str(uuid.uuid4())
        
        # Randomize severity
        insight["severity"] = random.choice(self.severity_levels)
        
        # Replace impacted device with random one from inventory
        if "impactedResources" in insight and insight["impactedResources"]:
            new_device = self.device_inventory.get_device()
            insight["impactedResources"] = [new_device]
        
        return insight
    
    def modify_breach_date_range(self, insight: Dict, min_days: int, max_days: int) -> Dict:
        """Modify the breach date to be within the specified range."""
        insight_copy = insight.copy()
        
        # Calculate new breach date within the range
        now = datetime.now(timezone.utc)
        days_to_add = random.randint(min_days, max_days)
        new_breach_date = now + timedelta(days=days_to_add)
        
        # Update breach date in ISO format with milliseconds
        breach_date_str = new_breach_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+00:00"
        insight_copy["breachDate"] = breach_date_str
        
        # Also update data.breachDate if it exists
        if "data" in insight_copy and "breachDate" in insight_copy["data"]:
            insight_copy["data"]["breachDate"] = breach_date_str
            
        return insight_copy

    def modify_breach_date_hours_with_minimum(self, insight: Dict, min_hours: int, max_hours: int, absolute_min_hours: int = 0) -> Dict:
        """Modify the breach date to be within the specified hour range with an absolute minimum."""
        insight_copy = insight.copy()
        
        # Calculate new breach date within the range, ensuring absolute minimum
        now = datetime.now(timezone.utc)
        hours_to_add = random.randint(min_hours, max_hours)
        
        # Ensure the breach date is at least absolute_min_hours from now
        if hours_to_add < absolute_min_hours:
            hours_to_add = absolute_min_hours
        
        new_breach_date = now + timedelta(hours=hours_to_add)
        
        # Update breach date in ISO format with milliseconds
        breach_date_str = new_breach_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+00:00"
        insight_copy["breachDate"] = breach_date_str
        
        # Also update data.breachDate if it exists
        if "data" in insight_copy and "breachDate" in insight_copy["data"]:
            insight_copy["data"]["breachDate"] = breach_date_str
            
        return insight_copy
    
    def modify_breach_date(self, insight: Dict, days_from_now: int) -> Dict:
        """Modify the breach date to be within the specified range."""
        insight_copy = insight.copy()
        
        # Calculate new breach date
        now = datetime.now(timezone.utc)
        new_breach_date = now + timedelta(days=random.randint(1, days_from_now))
        
        # Update breach date in ISO format with milliseconds
        breach_date_str = new_breach_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+00:00"
        insight_copy["breachDate"] = breach_date_str
        
        # Also update data.breachDate if it exists
        if "data" in insight_copy and "breachDate" in insight_copy["data"]:
            insight_copy["data"]["breachDate"] = breach_date_str
            
        return insight_copy
    
    def modify_updated_time_range(self, insight: Dict, min_hours: int, max_hours: int) -> Dict:
        """Modify the updated time to be within the past specified hour range."""
        insight_copy = insight.copy()
        
        # Calculate new updated time within the range
        now = datetime.now(timezone.utc)
        hours_to_subtract = random.randint(min_hours, max_hours)
        new_updated_time = now - timedelta(hours=hours_to_subtract)
        # Update updated time in ISO format with milliseconds
        updated_time_str = new_updated_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+00:00"
        print(now , updated_time_str)
        insight_copy["updatedTime"] = updated_time_str
        
        return insight_copy
    
    def modify_updated_time(self, insight: Dict, hours_ago: int) -> Dict:
        """Modify the updated time to be within the past specified hours."""
        insight_copy = insight.copy()
        
        # Calculate new updated time
        now = datetime.now(timezone.utc)
        new_updated_time = now - timedelta(hours=random.randint(1, hours_ago))
        
        # Update updated time in ISO format with milliseconds
        updated_time_str = new_updated_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+00:00"
        insight_copy["updatedTime"] = updated_time_str
        
        return insight_copy
    
    def generate_forecast_insights(self, config: Dict):
        """Generate and post forecast insights."""
        forecast_config = config.get("forecast_insight", {})
        forecast_insights = self.load_insights_from_folder(self.forecast_dir)
        
        if not forecast_insights:
            print("Warning: No forecast insights found in forecast folder.")
            return
        
        # Next 0-7 hours (minimum 3 hours from now)
        next_0_to_7_count = forecast_config.get("next_0_to_7", 0)
        for _ in range(next_0_to_7_count):
            insight = self.get_round_robin_insight(forecast_insights, 'forecast_counter')
            if insight:
                insight = self.modify_insight_properties(insight)
                modified_insight = self.modify_breach_date_hours_with_minimum(insight, 3, 7, 3)
                self.client.post_insight(modified_insight, "FORECAST: Next 0-7 hours")
        
        # Next 7-30 days
        next_7_to_30_count = forecast_config.get("next_7_to_30", 0)
        for _ in range(next_7_to_30_count):
            insight = self.get_round_robin_insight(forecast_insights, 'forecast_counter')
            if insight:
                insight = self.modify_insight_properties(insight)
                modified_insight = self.modify_breach_date_range(insight, 7, 30)
                self.client.post_insight(modified_insight, "FORECAST: Next 7-30 days")
        
        # Next 30-90 days
        next_30_to_90_count = forecast_config.get("next_30_to_90", 0)
        for _ in range(next_30_to_90_count):
            insight = self.get_round_robin_insight(forecast_insights, 'forecast_counter')
            if insight:
                insight = self.modify_insight_properties(insight)
                modified_insight = self.modify_breach_date_range(insight, 30, 90)
                self.client.post_insight(modified_insight, "FORECAST: Next 30-90 days")
    
    def generate_current_insights(self, config: Dict):
        """Generate and post current insights."""
        current_count = config.get("present", 0)
        current_insights = self.load_insights_from_folder(self.current_dir)
        
        if not current_insights:
            print("Warning: No current insights found in current folder.")
            return
        
        for _ in range(current_count):
            insight = self.get_round_robin_insight(current_insights, 'current_counter')
            if insight:
                insight = self.modify_insight_properties(insight)
                self.client.post_insight(insight, "CURRENT: Active insights")
    
    def generate_past_insights(self, config: Dict):
        """Generate and post past insights."""
        past_config = config.get("past", {})
        past_insights = self.load_insights_from_folder(self.past_dir)
        
        if not past_insights:
            print("Warning: No past insights found in past folder.")
            return
        
        # Last 0-12 hours
        last_0_to_12_count = past_config.get("last_0_to_12", 0)
        for _ in range(last_0_to_12_count):
            insight = self.get_round_robin_insight(past_insights, 'past_counter')
            if insight:
                insight = self.modify_insight_properties(insight)
                modified_insight = self.modify_updated_time_range(insight, 0, 12)
                self.client.post_insight(modified_insight, "PAST: Last 0-12 hours")
        
        # Last 12-24 hours
        last_12_to_24_count = past_config.get("last_12_to_24", 0)
        for _ in range(last_12_to_24_count):
            insight = self.get_round_robin_insight(past_insights, 'past_counter')
            if insight:
                insight = self.modify_insight_properties(insight)
                modified_insight = self.modify_updated_time_range(insight, 12, 24)
                self.client.post_insight(modified_insight, "PAST: Last 12-24 hours")
        
        # Last 24-48 hours
        last_24_to_48_count = past_config.get("last_24_to_48", 0)
        for _ in range(last_24_to_48_count):
            insight = self.get_round_robin_insight(past_insights, 'past_counter')
            if insight:
                insight = self.modify_insight_properties(insight)
                modified_insight = self.modify_updated_time_range(insight, 24, 48)
                self.client.post_insight(modified_insight, "PAST: Last 24-48 hours")
    
    def run(self):
        """Main execution method."""
        print(f"Loading configuration from: {self.config_file}")
        config = self.load_config()
        
        print(f"Target endpoint: {self.client.get_endpoint()}")
        if self.client.has_token():
            print(f"Using Bearer token: {self.client.get_token_preview()}")
        else:
            print("No authentication token provided")
        print(self.device_inventory)
        print(f"Device inventory: {self.device_inventory.get_device_count()} devices loaded")
        print("=" * 50)
        
        # Generate forecast insights
        print("Generating forecast insights...")
        self.generate_forecast_insights(config)
        
        # Generate current insights
        print("\nGenerating current insights...")
        self.generate_current_insights(config)
        
        # Generate past insights
        print("\nGenerating past insights...")
        self.generate_past_insights(config)
        
        print("\n" + "=" * 50)
        print("Insight generation completed!")