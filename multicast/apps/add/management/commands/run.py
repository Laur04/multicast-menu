import json
import re
import requests


def run():
    results = []
    failed = False

    try:
        # Make a request to the looking glass.
        r = requests.get("http://13.215.113.216/")

        # Format the raw response text and split it into an array
        response = json.loads(r.text)["output"]
        results.append({
            "source": response["source"],
            "group": response["group"],
            "udp_port": response["udp_port"],
            "status": response["status"],
        })
    except:
        failed = True

    return (results, failed)
