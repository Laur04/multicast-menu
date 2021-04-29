import datetime
import json

from django.http import  HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import AddForm, DescriptionForm
from .models import Description, M_Source, Stream


def vlc(request, target, os):
    source, group = target.split('_')
    stream = get_object_or_404(Stream, source=source, group=group)

    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename="playlist.m3u"'
    response.write('amt://{}@{}'.format(source, group))
    if stream.udp_port:
        response.write(':{}'.format(stream.udp_port))

    return response


def downvote(request, target):
    source, group = target.split('_')
    stream = get_object_or_404(Stream, source=source, group=group)

    stream.downvote += 1
    stream.save()

    return redirect(reverse('home:show_video', kwargs={'target': target}))


def show_video(request, target):
    source, group = target.split('_')
    stream = get_object_or_404(Stream, source=source, group=group)

    form = DescriptionForm()
    if request.method == 'POST':
        form = DescriptionForm(request.POST)
        if form.is_valid():
            descript, created = Description.objects.get_or_create(stream=stream, description=form.cleaned_data['ans'])
            if not created:
                descript.upvote()
            return redirect(reverse('home:show_video', kwargs={'target': target}))
    elif request.is_ajax():
        user_entry = request.GET.get('description', None)
        get_object_or_404(Description, stream=stream, description=user_entry).upvote()
        return JsonResponse(dict())
    
    descriptions = [(d.votes, d.description) for d in Description.objects.filter(stream=stream).order_by("-votes")][:3]

    ctx = {
        'form': form,
        'descriptions': descriptions,
        'stream': stream,
        'source': source,
        'group': group,
        'target': target,
        'udp': stream.udp_port,
    }

    return render(request, 'home/play.html', context=ctx)


def add(request):
    form = AddForm()
    if request.method == 'POST':
        form = AddForm(request.POST)
        if form.is_valid():
            stream = form.save()
            Description.objects.create(stream=stream, description=form.cleaned_data["description"])
            return redirect(reverse('home:index'))
    
    return render(request, 'home/add.html', context={'form': form})


def index(request):
    active_streams = list()
    for s in Stream.objects.filter(active=True):
        description_list = sorted([(d.votes, d.description) for d in Description.objects.filter(stream=s)], key=lambda a: a[0], reverse=True)
        if not description_list:
            description_list.append((0, "No title available"))
        active_streams.append((s, description_list[0]))
    
    return render(request, 'home/index.html', context={'stream_list': active_streams})
