import ipwhois
import re
import requests
import time


def run(devices):
    BASE_URL = 'https://routerproxy.grnoc.iu.edu/internet2/'
    to_return = set()
    for ip in devices:
        print(ip)
        
        # Make a request to the looking glass, surrounded by pauses to avoid rate limits.
        time.sleep(2)
        r = requests.get(BASE_URL + '?method=submit&device=' + ip + '&command=show multicast&menu=0&arguments=route detail')
        time.sleep(2)

        # Format the raw response text and split it into an array
        new_text = re.sub(r'&[^\s]{2,4};|[\r]', '', r.text).split('\n')

        # Loop through the formatted raw response text to discover streams
        fields = dict()
        for line in new_text[1:-1]:
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
                fields[key] = value
            else:
                fields[line] = ""
    return to_return
