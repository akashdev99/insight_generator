"""
Device Inventory Management for AI-Ops Insights Generator

This module manages a collection of devices that can be used as impacted resources
in generated insights.
"""

import os
import random
import uuid
from typing import Dict, List
from dotenv import load_dotenv


class DeviceInventory:
    def __init__(self, device_count: int = None):
        """Initialize the device inventory with a specified number of devices."""
        # Load environment variables
        load_dotenv()
        
        # Use provided count or get from env, fallback to default
        if device_count is None:
            device_count = int(os.getenv('AIOPS_DEVICE_COUNT', '50'))
        
        # Device selection strategy (random or sequential)
        self.selection_mode = os.getenv('AIOPS_DEVICE_SELECTION', 'random').lower()
        self.sequential_counter = 0
        
        self.devices = self._generate_devices(device_count)
    
    def _generate_devices(self, count: int) -> List[Dict]:
        """Generate a list of devices with random names and UIDs."""
        devices = []
        
        # Device name prefixes for variety
        prefixes = [
            "firewall", "gateway", "router", "switch", "security", 
            "border", "core", "edge", "dmz", "internal",
            "external", "backup", "primary", "secondary", "main"
        ]
        
        # Location/site identifiers
        locations = [
            "hq", "dc1", "dc2", "site1", "site2", "branch1", "branch2",
            "east", "west", "north", "south", "central", "remote"
        ]
        
        for i in range(count):
            prefix = random.choice(prefixes)
            location = random.choice(locations)
            number = random.randint(1, 999)
            
            device = {
                "uid": str(uuid.uuid4()),
                "name": f"{prefix}_{location}_{number:03d}",
                "type": "FTD"  # Always FTD for now
            }
            devices.append(device)
        
        return devices
    
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