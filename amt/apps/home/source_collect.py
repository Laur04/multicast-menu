import datetime
import django
import ipwhois
import logging
import os
import re
import requests
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amt.settings")
django.setup()

from .models import Stream, M_Source


output = set()
BASE_URL = 'https://routerproxy.grnoc.iu.edu/internet2/'
for device in M_Source.objects.all():
    ip = device.ip
    r = requests.get(BASE_URL + '?method=submit&device=' + ip + '&command=show multicast&menu=0&arguments=route detail')
    new_text = re.sub(r'&[^\s]{2,4};|[\r]', '', r.text)
    s_new_text = new_text.split('\n')
    fields = dict()
    for i in range(1, len(s_new_text) - 1):
        s_line = s_new_text[i].split(':', 1)
        if s_line[0] == '':
            if 'Group' in fields:
                source = str(fields['Source']).split('/')[0]
                group = str(fields['Group'])
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

                if re.match("^[0-9.]+$", source) and source != '193.17.9.3':  # filter out IPv6, Eumsat
                    if pps > 100:
                        output.add((who_is, source, group, pps))
            fields = dict()
        else:
            fields[s_line[0]] = ''.join(s_line[1:])
    time.sleep(2)

for o in output:
    print(o)
    try:
        stream = Stream.objects.filter(source=o[1]).get(group=o[2])
        stream.pps = o[3]
        stream.active = True
        stream.last_found = datetime.datetime.now()
        stream.save()
        print('Update existing stream')
    except:
        new_stream = Stream(whois=o[0], source=o[1], group=o[2], pps=o[3], active=True)
        new_stream.save()
        print('Create new stream')
