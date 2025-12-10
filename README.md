# AI-Ops Insights Generator CLI Tool

A Python CLI tool that generates and posts AI-Ops insights to a platform endpoint based on forecast configuration.

## Features

- Reads a JSON configuration file to determine how many insights to generate
- Supports three types of insights:
  - **Forecast insights**: Posted with modified breach dates (7, 30, or 90 days in the future)
  - **Current insights**: Active insights posted as-is
  - **Past insights**: Resolved insights with modified update times (12, 24, or 48 hours ago)
- Randomly selects insights from corresponding folders
- Posts insights to configurable API endpoint

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables (optional):
```bash
cp .env.example .env
# Edit .env file with your configuration
```

3. Make the script executable (optional):
```bash
chmod +x insight_generator.py
```

## Usage

### Basic usage with default endpoint:
```bash
python insight_generator.py config.json
```

### Custom endpoint and token:
```bash
python insight_generator.py config.json --endpoint https://your-server.com/api/insights --token your_bearer_token
```

### Using environment variables:
```bash
# Set in .env file or export directly
export AIOPS_BASE_URL=https://your-aiops-platform.com
export AIOPS_TOKEN=your_bearer_token_here
python insight_generator.py config.json
```

### Dry run (show what would be posted without making API calls):
```bash
python insight_generator.py config.json --dry-run
```

### Clear all insights (requires confirmation):
```bash
python insight_generator.py --clear
```

### Clear all insights with custom endpoint:
```bash
python insight_generator.py --clear --endpoint https://your-server.com/api/insights --token your_bearer_token
```

### Tenant Loader (copy insights from one domain to another):
```bash
# Load insights from source domain and post to target domain (set via AIOPS_DOMAIN)
python insight_generator.py --load source-domain.com

# With custom token
python insight_generator.py --load source-domain.com --token your_bearer_token
```

### Help:
```bash
python insight_generator.py --help
```

## Configuration Format

The configuration file should follow this JSON structure:

```json
{
  "forecast_insight": {
    "next_0_to_7": 2,     # Number of insights for next 0-7 days
    "next_7_to_30": 5,    # Number of insights for next 7-30 days
    "next_30_to_90": 3    # Number of insights for next 30-90 days
  },
  "present": 4,           # Number of current active insights
  "past": {
    "last_0_to_12": 1,    # Number of insights resolved in last 0-12 hours
    "last_12_to_24": 3,   # Number of insights resolved in last 12-24 hours
    "last_24_to_48": 2    # Number of insights resolved in last 24-48 hours
  }
}
```

## Environment Configuration

The tool supports configuration through environment variables via a `.env` file:

- `AIOPS_DOMAIN`: Base URL for the AI-Ops platform (default: `http://localhost:4047`)
- `AEGIS_DOMAIN`: Base URL for Aegis API calls (optional, falls back to `AIOPS_DOMAIN`)
- `AIOPS_TOKEN`: Bearer token for authentication (optional)
- `AIOPS_DEVICE_SELECTION`: Device selection strategy - `random` or `sequential` (default: `random`)
- `INSIGHT_PICKER`: Insight selection strategy - `sequential` or `random` (default: `sequential`)
- `GENERATION_MODE`: Generation strategy - `device` or `insight` (default: `insight`)
- `AIOPS_DEVICE_COUNT`: Number of devices to use in device mode (default: `3`)

Example `.env` file:
```
AIOPS_DOMAIN=https://your-aiops-platform.com
AEGIS_DOMAIN=https://your-aegis-api.com
AIOPS_TOKEN=your_bearer_token_here
AIOPS_DEVICE_SELECTION=sequential
INSIGHT_PICKER=random
GENERATION_MODE=device
AIOPS_DEVICE_COUNT=5
```

## How It Works

1. **Device Inventory**:
   - Fetches real devices from API endpoint: `/aegis/rest/v1/services/targets/devices`
   - Uses query parameter `q=deviceType:FTDC` to filter for FTD devices
   - Extracts device `uid` and `name` from API response
   - Device selection strategy configurable via `AIOPS_DEVICE_SELECTION`:
     - `random`: Devices are picked randomly from inventory (default)
     - `sequential`: Devices are picked sequentially in round-robin fashion
   - All devices are treated as type "FTD" 
   - Devices are assigned to insights when posting based on selection strategy
   - Falls back to a default device if API call fails

2. **Generation Modes**:
   - **Insight Mode** (`GENERATION_MODE=insight`): Default behavior - generates all configured insights for each type across different devices
   - **Device Mode** (`GENERATION_MODE=device`): Generates all configured insight types for each specific device
     - Uses `AIOPS_DEVICE_COUNT` to specify number of devices (default: 3)
     - Creates complete insight profiles per device
     - Example: If you have 3 devices and config specifies 2 forecast + 1 current insights, it creates 9 total insights (3 per device)

3. **Insight Selection Strategy**:
   - Configurable via `INSIGHT_PICKER` environment variable:
     - `sequential`: Round-robin selection ensures even distribution of insight templates (default)
     - `random`: Random selection from available templates for more variety
   - Each insight type (forecast, current, past, non-capacity) maintains separate selection state

4. **Dynamic Property Modification**:
   - **UID**: Each posted insight gets a new unique identifier
   - **Severity**: Randomly assigned from "CRITICAL", "WARNING", or "INFORMATIONAL"
   - **Device**: Random device from inventory assigned to `impactedResources`
   - **DateTime Format**: All timestamps use format "YYYY-MM-DDTHH:MM:SS.sss+00:00"

4. **Forecast Insights**: 
   - Selected in round-robin from the `forecast/` folder
   - Modifies the `breachDate` field to be within the specified time range:
     - `next_0_to_7`: 0-7 days from now
     - `next_7_to_30`: 7-30 days from now  
     - `next_30_to_90`: 30-90 days from now
   - Posts the modified insights

5. **Current Insights**:
   - Selected in round-robin from the `current/` folder
   - Posts them with modified properties (UID, severity, device)

6. **Past Insights**:
   - Selected in round-robin from the `past/` folder
   - Modifies the `updatedTime` field to be within the past specified hour ranges:
     - `last_0_to_12`: 0-12 hours ago
     - `last_12_to_24`: 12-24 hours ago
     - `last_24_to_48`: 24-48 hours ago
   - Posts the modified insights

## API Endpoint

The tool constructs the full API endpoint by combining:
- Base URL from `AIOPS_BASE_URL` environment variable (default: `http://localhost:4047`)
- API path: `/api/platform/ai-ops-insights/v1/insights`

Final endpoint: `{AIOPS_BASE_URL}/api/platform/ai-ops-insights/v1/insights`

### Authentication

The tool supports Bearer token authentication:
- Set `AIOPS_TOKEN` environment variable, or
- Pass `--token` command line argument
- If no token is provided, requests are made without authentication

The endpoint expects POST requests with JSON payload containing the insight data.

### Tenant Loader Operation

The tenant loader functionality allows copying insights from one domain to another:

1. **Source Domain**: Fetches insights from the specified source domain using GET request
2. **Limit**: Retrieves up to 300 insights from the source
3. **Target Domain**: Posts each insight to the target domain (configured via `AIOPS_DOMAIN`)
4. **Progress Tracking**: Shows real-time progress and transfer statistics

Example tenant loader output:
```
📥 Loading insights from: source-domain.com
📤 Target domain: target-domain.com
📋 Fetching insights from source domain...
🌐 GET https://source-domain.com/api/platform/ai-ops-insights/v1/insights
📝 Query parameters: {'limit': 300}
✅ Successfully fetched 150 insights
📦 Found 150 insights to transfer
🔄 Processing insight 1/150: Critical VPN Alert
✓ Successfully posted insight [TENANT_LOAD: 1/150]: Critical VPN Alert
...
📊 Transfer Summary:
   ✅ Successfully transferred: 148
   ❌ Failed transfers: 2
   📈 Success rate: 98.7%
```

## Example Output

```
Loading configuration from: config.json
Target endpoint: http://localhost:4047/api/platform/ai-ops-insights/v1/insights
==================================================
Generating forecast insights...
✓ Successfully posted insight: RAVPN Forecast - Session Capacity Warning
✓ Successfully posted insight: VPN Throughput Forecast Alert
...

Generating current insights...
✓ Successfully posted insight: Active VPN Session Limit Reached
...

Generating past insights...
✓ Successfully posted insight: Resolved: VPN Connection Timeout Issue
...

==================================================
Insight generation completed!
```

## Error Handling

- Invalid JSON configuration files are handled gracefully
- Missing folders result in warnings but don't stop execution
- API errors are reported but don't stop the tool from processing remaining insights
- Network timeouts are handled with appropriate error messages

## Requirements

- Python 3.6+
- requests library
- python-dotenv library
- Valid insight JSON templates in the appropriate folders