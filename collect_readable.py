import requests
import re
import time
import ipwhois
import datetime

outfile = open('m2icast_output.txt', 'w+')

devices = [
  "162.252.70.255",
  "162.252.70.254",
  "64.57.28.243",
  "162.252.70.252",
  "162.252.70.251",
  "162.252.70.250",
  "64.57.28.241",
  "162.252.70.221",
  "64.57.28.250",
  "162.252.70.246",
  "162.252.70.193",
  "162.252.70.245",
  "162.252.70.244",
  "162.252.70.243",
  "162.252.70.242",
  "162.252.70.241",
  "64.57.28.244",
  "162.252.70.220",
  "162.252.70.240",
  "162.252.70.239",
  "64.57.28.245",
  "162.252.70.217",
  "64.57.28.248",
  "162.252.70.218",
  "162.252.70.236",
  "162.252.70.235",
  "162.252.70.216",
  "64.57.28.242",
  "162.252.70.233",
  "162.252.70.232",
  "162.252.70.231",
  "64.57.30.0",
  "162.252.70.229",
  "162.252.70.219",
  "64.57.28.246",
  "162.252.70.195",
  "64.57.28.247",
  "162.252.70.226",
  "64.57.30.1",
  "162.252.70.224",
  "162.252.70.223",
  "64.57.28.249",
  "64.57.28.252",
  "64.57.28.253",
  "162.252.70.200",
  "162.252.70.194"
]

BASE_URL = 'https://routerproxy.grnoc.iu.edu/internet2/'
for device in devices:
    ip = device
    time.sleep(2)
    r = requests.get(BASE_URL + '?method=submit&device=' + ip + '&command=show multicast&menu=0&arguments=route detail')
    time.sleep(2)
    new_text = re.sub(r'&[^\s]{2,4};|[\r]', '', r.text)
    s_new_text = new_text.split('\n')
    outfile.write("\n\n//////////////////////////////\n")
    outfile.write("Device: " + ip)
    outfile.write('\n' + str(s_new_text) + '\n')
    fields = dict()
    for i in range(1, len(s_new_text) - 1):
        s_line = s_new_text[i].split(':', 1)
        if s_line[0] == '':
            if 'Group' in fields:
                source = str(fields['Source']).split('/')[0]
                group = str(fields['Group'])

                upstream = str(fields['Upstreaminterface'])
                try:
                    time.sleep(2)
                    r = requests.get(BASE_URL + '?method=submit&device=' + ip + '&command=show interfaces&menu=0&arguments=' + upstream)
                    new_text = re.sub(r'&[^\s]{2,4};|[\r]', '', r.text)
                    up_name = new_text[new_text.index('Description') + 12:new_text.index('Flags')]
                    time.sleep(2)
                except:
                    up_name = "Undefined"
                    pass

                downstream = "None"
                if 'Downstreaminterfacelist' in fields.keys():
                    downstream = list(fields)[list(fields).index('Downstreaminterfacelist') + 1]
                    down_list = []
                    names_list = []
                    if downstream.count('.') > 1:
                        down_list.append(downstream[:8])
                        down_list.append(downstream[8:])
                    else:
                        down_list.append(downstream)
                    for d in down_list:
                        try:
                            time.sleep(2)
                            r = requests.get(BASE_URL + '?method=submit&device=' + ip + '&command=show interfaces&menu=0&arguments=' + d)
                            new_text = re.sub(r'&[^\s]{2,4};|[\r]', '', r.text)
                            up_name = new_text[new_text.index('Description') + 12:new_text.index('Flags')]
                            names_list.append(up_name)
                            time.sleep(2)
                        except:
                            names_list.append("Undefined")
                down_string = ''.join(['{} ({})'.format(names_list[i], down_list[i]) for i in range(len(down_list))])

                st = fields['Statistics'].split(',')
                pps = int(re.sub(r'[^0-9]', '', st[1]))
                whois = ipwhois.IPWhois(source.split('/')[0])
                info = whois.lookup_rdap()
                asn_desc = info['asn_description']
                desc = None
                if info['network']['remarks'] is not None:
                    desc = info['network']['remarks'][0]['description']
                if asn_desc is not None:
                    who_is = asn_desc
                else:
                    who_is = desc
                
                outfile.write("\n*****************\nDiscovered Stream: {}, Source: {}, Group: {}, PPS: {}, IIF: {} ({}), OIL: {}\n".format(who_is, source, group, pps, up_name, upstream, down_string))
                if re.match("^[0-9.]+$", source) and source != '193.17.9.3':  # filter out IPv6, Eumsat
                    if pps > 100:
                        outfile.write("Stream kept for display on site.")
                    else:
                        outfile.write("Stream filtered out because PPS is less than or equal to 100.")
                else:
                    outfile.write("Stream filtered out because it is either Eumsat or IPv6.")
            fields = dict()
        else:
            fields[s_line[0]] = ''.join(s_line[1:])

outfile.close()
