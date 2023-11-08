#!/usr/bin/env python3
import os
import sys
import json
import requests

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
        monikers = json.load(f)
    for rpc in rpcs:
        print(f"polling {rpc}")
        net_info_res = requests.get(f"{rpc}/net_info")
        if net_info_res.status_code != 200:
            print(f"invalid status: {net_info_res.status_code}")
            continue
        net_info = net_info_res.json()
        current_monikers = [peer["node_info"]["moniker"] for peer in net_info["result"]["peers"]]
        new_monikers = [m for m in current_monikers if m not in monikers]
        if len(new_monikers) > 0:
            print(f"new monikers: {new_monikers}")
            monikers.extend(new_monikers)
            with open(db_path, "w") as f:
                json.dump(monikers, f)
            for m in new_monikers:
                try:
                    res = requests.post(slack_webhook_url, json={"text": f"new moniker: {m}"})
                    res.raise_for_status()
                except Exception as err:
                    print(f"error posting to slack: {err}")
    time.sleep(poll_seconds)