#!/usr/bin/env python3
import os
import sys
import json
import time
import requests

def notify_slack_peer_data(webhook_url, title, moniker, id, address, rpc):
    try:
        res = requests.post(
            webhook_url,
            json={
                "text": f"{title}: {moniker}",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{title}*",
                        },
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"_Moniker_\n{moniker}"},
                            {"type": "mrkdwn", "text": f"_Id_\n{id}"},
                            {"type": "mrkdwn", "text": f"_Address_\n{address}"},
                            {"type": "mrkdwn", "text": f"_Rpc_\n{rpc}"},
                        ],
                    },
                ],
            },
        )
        res.raise_for_status()
    except Exception as err:
        print(f"error posting to slack: {err}")
    time.sleep(0.01)

print("starting moniker monitor")
slack_webhook_url = os.environ["SLACK_WEBHOOK_URL"]
if len(sys.argv) < 2:
    config_path = "config.json"
else:
    config_path = sys.argv[1]
with open(config_path) as f:
    config = json.load(f)
db_path = config["db_file"]
rpcs = config["rpcs"]
poll_seconds = config.get("poll_seconds", 60)
if len(rpcs) == 0:
    print("no rpcs configured")
    sys.exit(1)
if not os.path.exists(db_path):
    print("initializing db")
    with open(db_path, "w") as f:
        json.dump([], f)
while True:
    with open(db_path) as f:
        peers = json.load(f)
    for rpc in rpcs:
        print(f"polling {rpc}")
        net_info_res = requests.get(f"{rpc}/net_info")
        if net_info_res.status_code != 200:
            print(f"invalid status: {net_info_res.status_code}")
            continue
        net_info = net_info_res.json()
        current_peers = {
          peer["node_info"]["moniker"]: {"id": peer["node_info"]["id"], "address": peer["remote_ip"]}
          for peer in net_info["result"]["peers"]
        }
        new_peers = {
          moniker: data
          for moniker, data in current_peers.items()
          if moniker not in peers
        }
        for moniker, data in new_peers.items():
          peers[moniker] = data
          notify_slack_peer_data(slack_webhook_url, "New Peer", moniker, data["id"], data["address"], rpc)
        if len(new_peers) > 0:
            with open(db_path, "w") as f:
                json.dump(peers, f)
    time.sleep(poll_seconds)
