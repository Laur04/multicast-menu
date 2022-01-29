import re
import celery
import os
import psutil
import signal

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from ..add.forms import AddByManualForm
from ..add.models import ManualReport, StreamSubmission
from ..add.tasks import verify_manual_report
from ..view.models import Stream
from .forms import ClaimForm


# Allows an authenticated user to view all of the streams that they have submitted through the platform
@login_required
def manage_index(request):
    
    context = {
        "reports": ManualReport.objects.filter(owner=request.user),
        "submissions": StreamSubmission.objects.filter(owner=request.user),
        "claimed": Stream.objects.filter(owner=request.user, submission_method="3")
    }

    return render(request, "manage/index.html", context=context)


# Allows an authenticated user to stop a stream
@login_required
def stop_stream(request, submission_id):
    submission = get_object_or_404(StreamSubmission.objects.filter(owner=request.user), id=submission_id)

    children = ""
    try:
        children = psutil.Process(int(submission.task_pid)).children(recursive=True)
    except:
        pass
    try:
        os.killpg(int(submission.task_pid), signal.SIGKILL)
    except:
        pass
    for child in children:
        try:
            child.kill()
        except psutil.NoSuchProcess:
            pass
    celery.task.control.revoke(submission.celery_task_id, terminate=True)

    submission.active = False
    submission.save()

    return redirect(reverse("manage:manage_index"))


# Allows an authenticated user to remove a manually reported stream entry
@login_required
def remove_stream(request, stream_id):
    stream = get_object_or_404(Stream.objects.filter(owner=request.user), stream_id)

    stream.delete()

    return redirect(reverse("manage:manage_index"))


# Allows an authenticated user to edit the information about their stream
@login_required
def edit_stream(request, stream_id):
    stream = get_object_or_404(Stream.objects.filter(owner=request.user), stream_id)
    form = AddByManualForm(instance=stream)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect(reverse("manage:manage_index"))


    return render(request, "manage/edit.html", context={"stream": stream})


# Allows an authenticated user to claim a stream created by a translation server using an access code
@login_required
def claim_stream(request):
    form = ClaimForm()

    if request.method == "POST":
        form = ClaimForm(request.POST)
        if form.is_valid():
            try:
                stream = Stream.objects.get(access_code=form.cleaned_data["access_code"])
                stream.owner = request.user
                stream.save()
                return redirect(reverse("manage:manage_index"))
            except:
                form.errors.add("That stream doesn't exist.")

    return render(request, "manage/claim.html", context={"form": form})


# Allows an authenticated user to retry verifying a manual report
@login_required
def retry_verification(request, report_id):
    report = get_object_or_404(ManualReport.objects.filter(owner=request.user), id=report_id)
    verify_manual_report.delay(report.id)

    return redirect(reverse("manage:manage_index"))
