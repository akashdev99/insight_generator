"""
Device Inventory Management for AI-Ops Insights Generator

This module manages a collection of devices that can be used as impacted resources
in generated insights. Devices are fetched from the API endpoint.
"""

import os
import random
import requests
from typing import Dict, List
from dotenv import load_dotenv


class DeviceInventory:
    def __init__(self, endpoint: str = None, token: str = None):
        """Initialize the device inventory by fetching devices from API endpoint."""
        # Load environment variables
        load_dotenv()
        
        # Use AEGIS_DOMAIN for aegis API calls, fallback to provided endpoint or AIOPS_DOMAIN
        self.aegis_endpoint = os.getenv('AEGIS_DOMAIN') or endpoint or os.getenv('AIOPS_DOMAIN', 'https://api.example.com')
        self.token = token or os.getenv('AIOPS_TOKEN')
        
        # Device selection strategy (random or sequential)
        self.selection_mode = os.getenv('AIOPS_DEVICE_SELECTION', 'random').lower()
        self.sequential_counter = 0
        
        # Fetch devices from API
        self.devices = self._fetch_devices_from_api()
        
        if not self.devices:
            print("Warning: No devices fetched from API. Using fallback device.")
            self.devices = self._create_fallback_device()
    
    def _fetch_devices_from_api(self) -> List[Dict]:
        """Fetch devices from the API endpoint."""
        try:
            # Construct the API URL using aegis_endpoint
            api_url = f"{self.aegis_endpoint.rstrip('/')}/aegis/rest/v1/services/targets/devices"
            
            # Set up headers
            headers = {}
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'
            
            # Set up query parameters
            params = {
                'q': 'deviceType:FTDC',
                'limit': os.getenv('AIOPS_DEVICE_COUNT', '50')
            }
            
            print(f"Fetching devices from: {api_url}")
            response = requests.get(api_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            devices = []
            
            # Extract device information from API response
            # Assuming the API returns a list of devices or devices in a 'data' field
            device_list = data if isinstance(data, list) else data.get('data', data.get('items', []))
            
            for device_data in device_list:
                device = {
                    "uid": device_data.get('uid') or device_data.get('id'),
                    "name": device_data.get('name'),
                    "type": "FTD"  # Always FTD as specified
                }
                
                # Only add devices with valid uid and name
                if device["uid"] and device["name"]:
                    devices.append(device)
            
            print(f"Successfully fetched {len(devices)} devices from API")
            return devices
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching devices from API: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error fetching devices: {e}")
            return []
    
    def _create_fallback_device(self) -> List[Dict]:
        """Create a fallback device if API fetch fails."""
        return [{
            "uid": "fallback-device-001",
            "name": "fallback_ftd_device",
            "type": "FTD"
        }]
    
    def get_device(self) -> Dict:
        """Get a device based on the configured selection strategy."""
        if self.selection_mode == 'sequential':
            return self.get_sequential_device()
        else:
            return self.get_random_device()
    
    def get_random_device(self) -> Dict:
        """Get a random device from the inventory."""
        return random.choice(self.devices).copy()
    
    def get_sequential_device(self) -> Dict:
        """Get devices sequentially one after the other."""
        device = self.devices[self.sequential_counter % len(self.devices)].copy()
        self.sequential_counter += 1
        return device
    
    def get_all_devices(self) -> List[Dict]:
        """Get a copy of all devices in the inventory."""
        return [device.copy() for device in self.devices]
    
    def get_device_count(self) -> int:
        """Get the total number of devices in the inventory."""
        return len(self.devices)