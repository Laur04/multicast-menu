from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse

import json

from .models import M_Source, Stream, Description
from .forms import AddForm, DescriptionForm

def vlc(request, target, os):
    target = target.split('_')
    source = target[0]
    group = target[1]
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
    
    return HttpResponseRedirect(reverse('home:show_video', kwargs={'target':target}))

def show_video(request, target):
    target_1 = target.split('_')
    source = target_1[0]
    group = target_1[1]
    stream = Stream.objects.filter(source=source).get(group=group)
    whois = stream.whois
    if request.method == 'POST':
        form = DescriptionForm(request.POST)
        if form.is_valid():
            try:
                descript = Description.objects.filter(stream=stream).get(description=form.cleaned_data['ans'])
                descript.upvote()
            except:           
                new_description = Description(stream=stream, description=form.cleaned_data['ans'], votes=0)
                new_description.save()
            return HttpResponseRedirect(reverse('home:show_video', kwargs={'target':target}))
    elif request.is_ajax():
        d = request.GET.get('description', None)
        descript = Description.objects.filter(stream=stream).get(description=d)
        descript.upvote()
        data = {}
        return JsonResponse(data)
    else:
        form = DescriptionForm()
    description_list = list()
    for d in Description.objects.filter(stream=stream):
        description_list.append((d.votes, d.description))
    ordered_list = sorted(description_list, key=lambda a: a[0], reverse=True)
    if len(ordered_list) > 3:
        ordered_list = [ordered_list[0], ordered_list[1], ordered_list[2]]
    return render(request, 'home/play.html', context={'source':source, 'group':group, 'whois':whois, 'form':form, 'descriptions':ordered_list})

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
