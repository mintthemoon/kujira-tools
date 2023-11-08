# moniker-monitor

## Overview
`moniker-monitor` is a Python program designed to monitor the RPC endpoints of a CometBFT blockchain network. It tracks new peers joining the network and notifies a configured Slack channel using a webhook.

## Features
- Polls multiple RPC endpoints at configurable intervals.
- Identifies new peers in the network.
- Sends notifications to Slack with peer details.
- Maintains a local database of known peers to track newcomers.

## Requirements
- Python 3
- `requests` library
- Slack webhook URL

## Setup
1. Install the required Python `requests` library if not already installed:
   ```
   pip install requests
   ```
2. Set the `SLACK_WEBHOOK_URL` environment variable with your Slack webhook URL.

## Configuration
Create a `config.json` file with the following structure:
```json
{
  "db_file": "path/to/local/db.json",
  "rpcs": ["http://rpc1.endpoint", "http://rpc2.endpoint"],
  "poll_seconds": 60
}
```
- `db_file`: Path to the local JSON database file to store known peers.
- `rpcs`: List of RPC endpoint URLs to monitor.
- `poll_seconds`: Interval in seconds between each poll (default is 60 seconds).

## Usage
Run the script with the following command:
```
python3 monitor.py [path_to_config_file]
```
If no configuration file path is provided, it defaults to `config.json` in the current directory.

## Notifications
When a new peer is detected, the following information is sent to the configured Slack channel:
- Peer's Moniker
- Peer's ID
- Peer's Address
- RPC endpoint URL
