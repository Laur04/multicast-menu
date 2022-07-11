from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import DescriptionForm, CustomUserCreationForm
from .models import Category, Description, Stream


def is_ajax(request):
    """
    Calling request.is_ajax() results in the following error:
        AttributeError: 'WSGIRequest' object has no attribute 'is_ajax'
    This function reproduces the functionality of request.is_ajax() without the error.

    References:
        AttributeError: 'WSGIRequest' object has no attribute 'is_ajax',
        https://stackoverflow.com/questions/70419441/attributeerror-wsgirequest-object-has-no-attribute-is-ajax

    :param request:
    :return:
    """
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


# Allow a user to create an account
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("login"))
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/register.html", context={"form": form})


# Home page listing all active streamseported_index
def index(request):
    # Get all categories from the database
    categories = Category.objects.all()
    # Get the active category from the request, defaulting to empty string if there is no category
    str_active_category = request.GET.get("category", "")
    # Get all active streams from the database
    stream_list = Stream.objects.filter(active=True).order_by("-created_at")

    if str_active_category:
        # Get a query set with the active category from the database
        active_category_set = categories.filter(slug=str_active_category)
        # Get the distinct streams with categories in the active category set
        stream_list = stream_list.filter(categories__in=active_category_set).distinct()

    # Get the search query from the request
    str_query = request.GET.get("query", "")
    if str_query:
        stream_list = stream_list.filter(description__icontains=str_query)

    # Show 24 streams per page
    paginator = Paginator(stream_list, 24)
    # Get the requested page number
    page_number = request.GET.get("page")
    # Get the page from the request
    page_obj = paginator.get_page(page_number)

    context = {
        "categories": categories,
        "active_category": str_active_category,
        "page_obj": page_obj,
        "query": str_query
    }
    return render(request, "view/index.html", context)


# Detail page for a specific stream
def detail(request, stream_id):
    stream = get_object_or_404(Stream, id=stream_id)

    context = {
        "stream": stream,
        "descriptions": Description.objects.filter(stream=stream).order_by("-votes")[:3],
        "description_form": DescriptionForm() if request.user.is_authenticated else None,
        "num_likes": stream.likes.count(),
        "stream_is_liked_by_user": request.user.is_authenticated and stream.likes.contains(request.user),
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

    return response


# Allow users to report broken streams
def report(request, stream_id):
    stream = get_object_or_404(Stream, id=stream_id)

    if is_ajax(request):
        stream.report()
        return JsonResponse(dict())
    else:
        raise Http404


# Allow users to upvote a description
def upvote_description(request, description_id):
    description = get_object_or_404(Description, id=description_id)

    if is_ajax(request):
        description.upvote()
        return JsonResponse(dict())


# Allow users to downvote a description
def downvote_description(request, description_id):
    description = get_object_or_404(Description, id=description_id)

    if is_ajax(request):
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
        if is_ajax(request):
            stream.report_count = 0
            stream.active = True
            stream.update_last_found()
            stream.save()
            return JsonResponse(dict())
        return Http404
    raise PermissionDenied


@login_required()
def set_editors_choice(request, stream_id):
    if request.user.is_superuser:
        stream = get_object_or_404(Stream, id=stream_id)
        if is_ajax(request):
            value = request.GET.get("editors_choice", "false")
            if value == "true":
                stream.editors_choice = True
                stream.save()
            else:
                stream.editors_choice = False
                stream.save()
            return JsonResponse(dict())
        return Http404
    raise PermissionDenied


@login_required()
def like_stream(request, stream_id):
    if request.user.is_authenticated:
        stream = get_object_or_404(Stream, id=stream_id)
        if is_ajax(request):
            if not stream.likes.contains(request.user):
                stream.likes.add(request.user)
            return JsonResponse(dict())
        return Http404
    raise PermissionDenied


@login_required()
def remove_like_from_stream(request, stream_id):
    if request.user.is_authenticated:
        stream = get_object_or_404(Stream, id=stream_id)
        if is_ajax(request):
            if stream.likes.contains(request.user):
                stream.likes.remove(request.user)
            return JsonResponse(dict())
        return Http404
    raise PermissionDenied
