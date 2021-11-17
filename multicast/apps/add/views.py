from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect, render
from django.urls import reverse

from ...utils import create_random_file_path
from ..view.models import Stream
from .forms import AddByFileForm, AddByLinkForm, AddByManualForm
from .models import StreamSubmission
from .tasks import submit_file_to_translator, submit_link_to_translator, verify_manual_report


# Index page for add where an authenticated user can select how they would like to add a stream
@login_required
def add_index(request):
    return render(request, "add/add_index.html")


# Allows an authenticated user to upload a file to be streamed
@login_required
def add_stream_file(request):
    form = AddByFileForm()
    if request.method == "POST":
        form = AddByFileForm(request.POST, request.FILES)
        if form.is_valid():
            random_path = "{}/{}".format(settings.MEDIA_ROOT, create_random_file_path())
            fs = FileSystemStorage()
            fs.save(random_path, form.cleaned_data["file_to_stream"])
            ss = StreamSubmission.objects.create(
                owner = request.user,
                path_to_uploaded_file = random_path,
            )
            submit_file_to_translator.delay(ss)
            return redirect(reverse("manage:manage_index"))

    return render(request, "add/add_file.html", context={"form": form})


# Allows an authenticated user to specify a link to pull streamed video from
@login_required
def add_stream_link(request):
    form = AddByLinkForm()
    if request.method == "POST":
        form = AddByFileForm(request.POST, request.FILES)
        if form.is_valid():
            random_path = "{}/{}".format(settings.MEDIA_ROOT, create_random_file_path())
            ss = StreamSubmission.objects.create(
                owner = request.user,
                path_to_uploaded_file = random_path,
                url_to_streamed_video = form.cleaned_data["link_to_stream"],
            )
            submit_link_to_translator.delay(ss)
            return redirect(reverse("manage:manage_index"))

    return render(request, "add/add_file.html", context={"form": form})


# Allows an authenticated user to manually report a stream
@login_required
def add_stream_manual(request):
    form = AddByManualForm()
    if request.method == "POST":
        form = AddByManualForm(request.POST)
        if form.is_valid():
            report = form.save()
            report.owner = request.user
            report.save()
            verify_manual_report.delay(report)
            return redirect(reverse("manage:manage_index"))
    
    return render(request, "add/add_manual.html", context={"form": form})
