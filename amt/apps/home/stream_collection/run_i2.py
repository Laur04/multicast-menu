import ipwhois
import re
import requests
import time


def run(devices):
    BASE_URL = 'https://routerproxy.grnoc.iu.edu/internet2/'
    to_return = set()
    sources = dict()
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
                fields[key] = value
            else:
                fields[line] = ""
    return to_return
