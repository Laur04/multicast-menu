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
    RELAY_LIST = ((0, "amt-relay.m2icast.net"), (1, "amt-relay.geant.org"), (2, "Other (please specify)"))

    form = ManualSubmissionForm(data_list=RELAY_LIST)

    if request.method == "POST":
        form = ManualSubmissionForm(request.POST, data_list=RELAY_LIST)
        if form.is_valid():
            stream = form.save()
            stream.owner = request.user
            stream.active = False
            stream.collection_method = "02"
            stream.amt_relay = RELAY_LIST[int(form.cleaned_data["amt_relay"])][1]
            stream.save()

            if int(form.cleaned_data["amt_relay"]) == 2:
                stream.amt_relay = form.cleaned_data["amt_relay_other"]
                stream.save()

            report = ManualSubmission.objects.create(
                stream=stream,
                active=False,
            )
            report.celery_id = verify_manual_report.delay(stream.id).id
            report.save()

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

            upload = UploadSubmission.objects.create(
                stream=stream,
                active=False,
                uploaded_file=random_path,
                access_code=create_random_string(40),
            )
            upload.celery_id = submit_file_to_translator.delay(stream.id).id
            upload.save()

            return redirect(reverse("manage:index"))

    return render(request, "add/add_upload.html", context={"form": form})
