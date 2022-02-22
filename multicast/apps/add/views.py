from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect, render
from django.urls import reverse

from ...utils import create_random_string
from .forms import ManualSubmissionForm, UploadSubmissionForm
from .models import ManualSubmission, UploadSubmission
from .tasks import submit_file_to_translator, verify_manual_report


# Index page for add where an authenticated user can select how they would like to add a stream
@login_required
def index(request):
    return render(request, "add/index.html")


# Allows an authenticated user to manually report a stream
@login_required
def add_manual(request):
    form = ManualSubmissionForm()

    if request.method == "POST":
        form = ManualSubmissionForm(request.POST)
        if form.is_valid():
            stream = form.save()
            stream.owner = request.user
            stream.active = False
            stream.collection_method = "02"
            stream.save()

            ManualSubmission.objects.create(
                stream=stream,
                celery_id=verify_manual_report.delay(stream.id).id,
                active=False,
            )

            return redirect(reverse("manage:index"))
    
    return render(request, "add/add_manual.html", context={"form": form})


# Allows an authenticated user to upload a file to be streamed
@login_required
def add_upload(request):
    form = UploadSubmissionForm()

    if request.method == "POST":
        form = UploadSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            stream = form.save()
            stream.owner = request.user
            stream.active = False
            stream.collection_method = "03"
            stream.save()

            random_path = "{}/{}".format(settings.MEDIA_ROOT, create_random_string(40))
            fs = FileSystemStorage()
            fs.save(random_path, form.cleaned_data["file_to_stream"])

            UploadSubmission.objects.create(
                stream=stream,
                celery_id=submit_file_to_translator.delay(stream.id).id,
                active=False,
                uploaded_file=random_path,
                access_code=create_random_string(40),
            )

            return redirect(reverse("manage:index"))

    return render(request, "add/add_upload.html", context={"form": form})
