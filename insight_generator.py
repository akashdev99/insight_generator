#!/usr/bin/env python3
"""
AI-Ops Insights Generator CLI Tool

This tool reads a forecast JSON configuration and generates insights
by posting them to the AI-Ops platform endpoint.
"""

import argparse
import os
import sys
from src.service import InsightGenerator, InsightClearer, InsightMigrator
from dotenv import load_dotenv

def main():
    load_dotenv()
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
    parser.add_argument(
        "--load",
        metavar="SOURCE_DOMAIN",
        help="Load insights from source domain and post to target domain (set via AIOPS_DOMAIN)"
    )
    
    args = parser.parse_args()
    
    # Handle clear insights operation
    if args.clear:
        clearer = InsightClearer(args.endpoint, args.token, args.dry_run)
        success = clearer.clear_with_confirmation()
        
        if success:
            print("✓ Successfully cleared all insights.")
        else:
            print("✗ Failed to clear insights.")
            sys.exit(1)
        return
    
    # Handle tenant loader operation
    if args.load:
        migrator = InsightMigrator(args.endpoint, args.token, args.dry_run)
        success = migrator.migrate_insights(args.load)
        
        if success:
            print("✓ Successfully completed tenant loading operation.")
        else:
            print("✗ Tenant loading operation failed.")
            sys.exit(1)
        return
    
    # Validate config file exists (only needed for generation operations)
    if not args.config_file:
        print("Error: Configuration file is required for insight generation.")
        print("Use --help to see available options.")
        sys.exit(1)
        
    if not os.path.isfile(args.config_file):
        print(f"Error: Configuration file '{args.config_file}' does not exist.")
        sys.exit(1)
    
    # Create and run the insight generator
    generator = InsightGenerator(args.config_file, args.endpoint, args.token, args.dry_run)
    generator.run()


if __name__ == "__main__":
    main()