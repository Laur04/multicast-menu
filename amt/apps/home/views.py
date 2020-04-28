from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse

import json
import datetime
import ipwhois

from .models import M_Source, Stream, Description
from .forms import AddForm, DescriptionForm

def vlc(request, target, os):
    target = target.split('_')
    source = target[0]
    group = target[1]
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename="playlist.m3u"'
    response.write('amt://' + source + '@' + group)
    return response

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
        a = request.GET.get('description', None)
        a = a.split('_')
        d = a[0]
        source = a[1]
        group = a[2]
        stream = Stream.objects.filter(source=source).get(group=group)
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
            source = form.cleaned_data['source']
            group = form.cleaned_data['group']
            description = form.cleaned_data['description']
            try:
                stream = Stream.objects.filter(source=source).get(group=group)
                stream.active = True
                stream.last_found = datetime.datetime.now()
                stream.save()
                try:
                    descript = Description.objects.filter(stream=stream).get(description=description)
                    descript.upvote()
                except:
                    new_description = Description(stream=stream, description=description, votes=0)
                    new_description.save()
                return HttpResponseRedirect(reverse('home:index'))
            except:
                try:
                    whois = ipwhois.IPWhois(source)
                    info = whois.lookup_rdap()
                    asn_desc = info['asn_description']
                    desc = None
                    if info['network']['remarks'] is not None:
                        desc = info['network']['remarks'][0]['description']
                    if asn_desc is not None:
                        who_is = asn_desc
                    else:
                        who_is = desc
                    new_stream = Stream(whois=who_is, source=source, group=group, active=True)
                    new_stream.save()
                    new_description = Description(stream=new_stream, description=description, votes=0)
                    new_description.save()
                    return HttpResponseRedirect(reverse('home:index'))
                except:
                    return render(request, 'home/add.html', context={'form':form, 'error':True})
    else:
        form = AddForm()
        return render(request, 'home/add.html', context={'form':form})

def index(request):
    active_streams = list()
    for s in Stream.objects.filter(active=True):
        description_list = list()
        for d in Description.objects.filter(stream=s):
            description_list.append((d.votes, d.description))
        to_show = None
        if description_list:
            ordered_list = sorted(description_list, key=lambda a: a[0], reverse=True)
            to_show = ordered_list[0]
            active_streams.append((s, to_show))
        else:
            to_show = "No description available"
            active_streams.append((s, (0, to_show)))
    return render(request, 'home/index.html', context={'stream_list':active_streams})
