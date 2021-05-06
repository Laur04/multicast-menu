import ipwhois
import json
import re
import requests
import time


def run(outfile):
    BASE_URL = 'https://lg.geant.org/rest/submit'
    headers = {"accept": "application/json", "content-type": "application/json"}
    devices = [d.strip() for d in open("devices_geant.txt", "r").readlines()]
    sources = dict()
    for ip in devices:
        # Make a request to the looking glass, surrounded by pauses to avoid rate limits.
        time.sleep(2)
        data = {"selectedRouters":[{"name":ip}],"selectedCommand":{"value":"show multicast route extensive inet\""}}
        r = requests.post(BASE_URL, data=json.dumps(data), headers=headers)
        time.sleep(2)

        # Format the raw response text and split it into an array
        response = json.loads(r.text)["output"][ip]["commandResult"]
        response_text = [l.strip() for l in response.split('\n')]

        # Write information about the device to the output file
        outfile.write("##############\nDevice: {} (GEANT)\nRaw Output: {}\n\n".format(ip, ", ".join(response_text)))

        # Loop through the formatted raw response text to discover streams
        fields = dict()
        for line in response_text[1:-1]:
            # Begin parsing fields
            if line == '':
                if 'Group' in fields:
                    # Pull the source and group out to use
                    source = str(fields['Source']).split('/')[0]
                    group = str(fields['Group'])

                    # Attempt to discover the upstream interface
                    upstream_interface = str(fields['Upstream interface'])
                    try:
                        if upstream_interface in sources.keys():
                            upstream_interface_name = sources[upstream_interface]
                        else:
                            data = {"selectedRouters":[{"name":ip}],"selectedCommand":{"value":"show interface " + upstream_interface}} 
                            r = requests.post(BASE_URL, data=json.dumps(data), headers=headers)
                            response = json.loads(r.text)["output"][ip]["commandResult"]
                            upstream_interface_name = response[response.index('Description') + 12:response.index('Flags')].strip()
                            sources[upstream_interface] = upstream_interface_name
                    except:
                        upstream_interface_name = "Undefined"
                        pass
                    
                    # Attempt to discover downstream interfaces
                    downstream_interfaces_string = "None"
                    if 'Downstream interface list' in fields.keys():
                        downstream_interfaces = list(fields)[list(fields).index('Downstream interface list') + 1]
                        downstream_interfaces_list = downstream_interfaces.split(" ")
                        interface_names = []
                        for interface in downstream_interfaces_list:
                            try:
                                if interface in sources.keys():
                                    interface_name = sources[interface]
                                else:
                                    data = {"selectedRouters":[{"name":ip}],"selectedCommand":{"value":"show interface " + interface}}
                                    r = requests.post(BASE_URL, data=json.dumps(data), headers=headers)
                                    response = json.loads(r.text)["output"][ip]["commandResult"]
                                    interface_name = response[response.index('Description') + 12:response.index('Flags')].strip()
                                    sources[interface] = interface_name
                                interface_names.append(interface_name)
                            except:
                                interface_names.append("Undefined")
                        downstream_interfaces_string = ', '.join(['{} ({})'.format(interface_names[i], downstream_interfaces_list[i]) for i in range(len(downstream_interfaces_list))])

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

                    # Decide how the site will treat this stream
                    site_decision = ""
                    if re.match("^[0-9.]+$", source) and source != '193.17.9.7':  # filter out IPv6, Eumsat
                        site_decision = "Stream kept for display on site." if pps > 100 else "Stream filtered out because PPS is less than or equal to 100."
                    else:
                       site_decision = "Stream filtered out because it is IPv6."

                    # Write this information about the discovered stream to the output file
                    outfile.write("*************\nDiscovered Stream: {}, Source: {}, Group: {}, PPS: {}, IIF: {} ({}), OIL: {}\n{}\n".format(
                            who_is,
                            source,
                            group,
                            pps,
                            upstream_interface_name,
                            upstream_interface,
                            downstream_interfaces_string,
                            site_decision
                        )
                    )

                    # Reset the fields dictionary
                    fields = dict()
            elif ":" in line:
                key, value = line.split(':', 1)
                fields[key.strip()] = value.strip()
            else:
                fields[line.strip()] = ""

        # Write formatting to the output file
        outfile.write("\n\n")
