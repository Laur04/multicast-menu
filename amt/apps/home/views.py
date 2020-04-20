from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse

import json

from .models import M_Source
from .forms import AddForm

import requests
import re
import time
import ipwhois

def vlc(request, target, os):
    target = target.split('_')
    source = target[0]
    group = target[1]
    new_source = source.split('/')[0]
    if os == 'linux':
        # make a .sh file
        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename="play_vlc.sh"'
        response.write('vlc amt://' + source + '@' + group)
    elif os == 'windows':
        # make a .bat file
        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename="play_vlc.bat"'
        response.write('"C:\\Program Files\\VideoLAN\\VLC\\vlc.exe" amt://' + source + '@' + group)
    elif os == 'mac':
        # make a .command file
        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename="play_vlc.command"'
        response.write('/Applications/VLC.app/Contents/MacOS/VLC -vvv amt://' + source + '@' + group + ' --amt-relay 162.250.136.101')
    if response:
        return response
    
    return render(request, 'home/play.html', context={'source':source, 'group':group, 'error':True})

def show_video(request, target):
    target = target.split('_')
    source = target[0]
    group = target[1]
    new_source = source.split('/')[0]
    return render(request, 'home/play.html', context={'source':source, 'group':group, 'error':False})

def add(request):
    if request.method == 'POST':
        form = AddForm(request.POST)
        if form.is_valid():
            repeat = False
            source_list = M_Source.objects.all()
            for s in source_list:
                if s.ip == form.cleaned_data['ip']:
                    repeat = True
            if not repeat:
                new_source = M_Source(ip=form.cleaned_data['ip'])
                new_source.save()
                return HttpResponseRedirect(reverse('home:index'))
        return render(request, 'home/add.html', context={'form':form, 'error':True})
    else:
        form = AddForm()
        return render(request, 'home/add.html', context={'form':form})

def index(request):
    if request.is_ajax():
        BASE_URL = 'https://routerproxy.grnoc.iu.edu/internet2/'

        device = request.GET.get('device', None)
        output = set()
        r = requests.get(BASE_URL + '?method=submit&device=' + device + '&command=show multicast&menu=0&arguments=route detail')
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
                    pps = int(re.sub(r'[^0-9]', '', st[2]))
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

                    if source != '193.17.9.3':  # filter out satellite data
                        if pps > 100:
                            output.add((who_is, source, group))
                fields = dict()
            else:
                fields[s_line[0]] = ''.join(s_line[1:])
        output = list(output)
        
        return JsonResponse({'streams':output})

    devices = list()
    for d in M_Source.objects.all():
        devices.append(d.ip)
    json_devices = json.dumps(devices)
    return render(request, 'home/index.html', context={'device_list':json_devices})
