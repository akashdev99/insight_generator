#!/usr/bin/env python3
"""
AI-Ops Insights Generator CLI Tool

This tool reads a forecast JSON configuration and generates insights
by posting them to the AI-Ops platform endpoint.
"""

import argparse
import os
import sys
from src.generator import InsightGenerator


def main():
    parser = argparse.ArgumentParser(
        description="AI-Ops Insights Generator CLI Tool"
    )
    parser.add_argument(
        "config_file",
        nargs="?",
        help="Path to the JSON configuration file (not required for --clear operation)"
    )
    parser.add_argument(
        "--endpoint",
        help="API endpoint URL (overrides AIOPS_BASE_URL env var)"
    )
    parser.add_argument(
        "--token",
        help="Bearer token for authentication (overrides AIOPS_TOKEN env var)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be posted without actually making API calls"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all insights from the platform (requires confirmation)"
    )
    
    args = parser.parse_args()
    
    # Handle clear insights operation
    if args.clear:
        # For clear operation, we don't need config file validation
        from src.client import AIOpsClient
        
        print("⚠️  WARNING: This will delete ALL insights from the platform!")
        confirmation = input("Are you sure you want to continue? (yes/no): ").lower().strip()
        
        if confirmation == 'yes':
            client = AIOpsClient(args.endpoint, args.token, args.dry_run)
            success = client.clear_all_insights()
            if success:
                print("✓ Successfully cleared all insights.")
            else:
                print("✗ Failed to clear insights.")
                sys.exit(1)
        else:
            print("Operation cancelled.")
        return
    
    # Validate config file exists (only needed for generation operations)
    if not os.path.isfile(args.config_file):
        print(f"Error: Configuration file '{args.config_file}' does not exist.")
        sys.exit(1)
    
    # Create and run the insight generator
    generator = InsightGenerator(args.config_file, args.endpoint, args.token, args.dry_run)
    generator.run()


if __name__ == "__main__":
    main()