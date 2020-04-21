from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse

import json

from .models import M_Source, Stream
from .forms import AddForm

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
    active_streams = Stream.objects.filter(active=True)
    return render(request, 'home/index.html', context={'stream_list':active_streams})
