import ipwhois
import json
import re
import requests
import time


def run(devices):
    BASE_URL = 'https://lg.geant.org/rest/submit'
    headers = {"accept": "application/json", "content-type": "application/json"}
    to_return = set()
    for ip in devices:
        print(ip)

        # Make a request to the looking glass, surrounded by pauses to avoid rate limits.
        time.sleep(2)
        data = {"selectedRouters":[{"name":ip}],"selectedCommand":{"value":"show multicast route extensive inet\""}}
        r = requests.post(BASE_URL, data=json.dumps(data), headers=headers)
        time.sleep(2)

        # Format the raw response text and split it into an array
        response = json.loads(r.text)["output"][ip]["commandResult"]
        response_text = [l.strip() for l in response.split('\n')]

        # Loop through the formatted raw response text to discover streams
        fields = dict()
        for line in response_text[1:-1]:
            # Begin parsing fields
            if line == '':
                if 'Group' in fields:
                    # Pull the source and group out to use
                    source = str(fields['Source']).split('/')[0]
                    group = str(fields['Group'])

                    # Pull out stream statistics
                    st = fields['Statistics'].split(',')
                    pps = int(re.sub(r'[^0-9]', '', st[1]))
                    info = ipwhois.IPWhois(source.split('/')[0].strip()).lookup_rdap(retry_count=10, rate_limit_timeout=1)
                    asn_desc = info['asn_description']
                    desc = info['network']['remarks'][0]['description'] if info['network']['remarks'] is not None else None
                    who_is = asn_desc if asn_desc is not None else desc

                    # Add information to to_return
                    to_return.add((source, group, who_is, pps))

                    # Reset the fields dictionary
                    fields = dict()
            elif ":" in line:
                key, value = line.split(':', 1)
                fields[key.strip()] = value.strip()
            else:
                fields[line.strip()] = ""
    return to_return
