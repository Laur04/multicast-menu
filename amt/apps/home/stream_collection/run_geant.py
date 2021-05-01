import ipwhois
import json
import re
import requests
import time
import whois


def run(devices):
    BASE_URL = 'https://lg.geant.org/rest/submit'
    headers = {"accept": "application/json", "content-type": "application/json"}
    to_return = set()
    sources = dict()
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

                    # Gather whois data
                    who_is = "Undefined"
                    formatted_source = source.split('/')[0].strip()
                    if formatted_source in sources.keys():
                        who_is = sources[formatted_source]
                    else:
                        who_is = ipwhois.IPWhois(formatted_source).lookup_whois()['asn_description']
                        sources[formatted_source] = who_is

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
