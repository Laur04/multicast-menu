import ipwhois
import re
import requests
import time


def run(outfile):
    BASE_URL = 'https://routerproxy.grnoc.iu.edu/internet2/'
    devices = [d.strip() for d in open("devices_i2.txt", "r").readlines()]
    for ip in devices:
        # Make a request to the looking glass, surrounded by pauses to avoid rate limits.
        time.sleep(5)
        r = requests.get(BASE_URL + '?method=submit&device=' + ip + '&command=show multicast&menu=0&arguments=route detail')
        time.sleep(5)

        # Format the raw response text and split it into an array
        new_text = re.sub(r'&[^\s]{2,4};|[\r]', '', r.text).split('\n')

        # Write information about the device to the output file
        outfile.write("##############\nDevice: {} (I2)\nRaw Output: {}\n\n".format(ip, ", ".join(new_text)))

        # Loop through the formatted raw response text to discover streams
        fields = dict()
        for line in new_text[1:-1]:
            # Begin parsing fields
            if line == '':
                if 'Group' in fields:
                    # Pull the source and group out to use
                    source = str(fields['Source']).split('/')[0]
                    group = str(fields['Group'])

                    # Attempt to discover the upstream interface
                    upstream_interface = str(fields['Upstreaminterface'])
                    try:
                        time.sleep(5)
                        r = requests.get(BASE_URL + '?method=submit&device=' + ip + '&command=show interfaces&menu=0&arguments=' + upstream_interface)
                        time.sleep(5)
                        
                        response = re.sub(r'&[^\s]{2,4};|[\r]', '', r.text)
                        upstream_interface_name = response[response.index('Description') + 12:response.index('Flags')].strip()
                    except:
                        upstream_interface_name = "Undefined"
                        pass
                    
                    # Attempt to discover downstream interfaces
                    downstream_interfaces_string = "None"
                    if 'Downstreaminterfacelist' in fields.keys():
                        downstream_interfaces = list(fields)[list(fields).index('Downstreaminterfacelist') + 1]
                        downstream_interfaces_list = downstream_interfaces.split(" ")
                        interface_names = []
                        for interface in downstream_interfaces_list:
                            try:
                                time.sleep(5)
                                r = requests.get(BASE_URL + '?method=submit&device=' + ip + '&command=show interfaces&menu=0&arguments=' + interface)
                                time.sleep(5)

                                response = re.sub(r'&[^\s]{2,4};|[\r]', '', r.text)
                                interface_name = response[response.index('Description') + 12:response.index('Flags')].strip()
                                interface_names.append(interface_name)
                            except:
                                interface_names.append("Undefined")
                        downstream_interfaces_string = ''.join(['{} ({})'.format(interface_names[i], downstream_interfaces_list[i]) for i in range(len(downstream_interfaces_list))])

                    # Pull out stream statistics
                    st = fields['Statistics'].split(',')
                    pps = int(re.sub(r'[^0-9]', '', st[1]))
                    info = ipwhois.IPWhois(source.split('/')[0]).lookup_rdap()
                    asn_desc = info['asn_description']
                    desc = info['network']['remarks'][0]['description'] if info['network']['remarks'] is not None else None
                    who_is = asn_desc if asn_desc is not None else desc

                    # Decide how the site will treat this stream
                    site_decision = ""
                    if re.match("^[0-9.]+$", source) and source != '193.17.9.3':  # filter out IPv6, Eumsat
                        site_decision = "Stream kept for display on site." if pps > 100 else "Stream filtered out because PPS is less than or equal to 100."
                    else:
                       site_decision = "Stream filtered out because it is either Eumsat or IPv6."

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
                fields[key] = value
            else:
                fields[line] = ""

        # Write formatting to the output file
        outfile.write("\n\n")
