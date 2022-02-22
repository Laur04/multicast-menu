from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import DescriptionForm
from .models import Description, Stream


# Allow a user to create an account
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("login"))
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", context={"form": form})


# Home page listing all active streamseported_index
def index(request):
    context = {
        "stream_list": Stream.objects.filter(active=True).order_by("report_count")
    }
    return render(request, "view/index.html", context=context)


# Detail page for a specific stream
def detail(request, stream_id):
    stream = get_object_or_404(Stream, id=stream_id)
    context = {
        "stream": stream,
        "descriptions": Description.objects.filter(stream=stream).order_by("-votes")[:3],
        "description_form": DescriptionForm() if request.user.is_authenticated else None,
    }

    return render(request, "view/detail.html", context=context)


# Download a .m3u file for the user to open in VLC
def open(request, stream_id):
    stream = get_object_or_404(Stream, id=stream_id)

    response = HttpResponse()
    response["Content-Disposition"] = 'attachment; filename="playlist.m3u"'
    response.write("amt://{}@{}".format(stream.source, stream.group))
    if stream.udp_port:
        response.write(":{}".format(stream.udp_port))
    if stream.amt_relay:
        response.write(" --amt-relay {}".format(stream.amt_relay))

    return response


# Allow users to report broken streams
def report(request, stream_id):
    stream = get_object_or_404(Stream, id=stream_id)

    if request.is_ajax():
        stream.report()
        return JsonResponse(dict())
    else:
        raise Http404


# Allow users to upvote a description
def upvote_description(request, description_id):
    description = get_object_or_404(Description, id=description_id)

    if request.is_ajax():
        description.upvote()
        return JsonResponse(dict())


# Allow users to downvote a description
def downvote_description(request, description_id):
    description = get_object_or_404(Description, id=description_id)

    if request.is_ajax():
        description.downvote()
        return JsonResponse(dict())


# Allow authenticated user to submit a stream description
@login_required
def submit_description(request, stream_id):
    stream = get_object_or_404(Stream, id=stream_id)

    if request.method == "POST":
        form = DescriptionForm(request.POST)
        if form.is_valid():
            description, created = Description.objects.get_or_create(
                stream=stream,
                text=form.cleaned_data["text"],
                defaults={
                    "user_submitted": request.user,
                }
            )
            if not created:
                description.upvote()    
        return redirect(reverse("view:detail", kwargs={"stream_id": stream.id}))
    raise Http404


# Allow admins to review broken streams
@login_required
def broken_index(request):
    if request.user.is_superuser:
        context = {
            "stream_list": Stream.objects.filter(active=False)
        }
        return render(request, "view/broken_index.html", context=context)
    raise PermissionDenied


# Allow admins to take action on broken streams
@login_required
def broken_detail(request, stream_id):
    if request.user.is_superuser:
        stream = get_object_or_404(Stream, id=stream_id)

        if request.method == "POST":
            stream.delete()
            return redirect(reverse("view:broken_index"))
        else:
            context = {
                "stream": stream,
                "descriptions": Description.objects.filter(stream=stream).order_by("-votes")[:3],
            }

            return render(request, "view/broken_detail.html", context=context)
    raise PermissionDenied


# Clear the reports and/or inactivity associated with a stream
@login_required
def broken_clear(request, stream_id):
    if request.user.is_superuser:
        stream = get_object_or_404(Stream, id=stream_id)
        if request.is_ajax():
            stream.report_count = 0
            stream.active = True
            stream.update_last_found()
            stream.save()
            return JsonResponse(dict())
        return Http404
    raise PermissionDenied
