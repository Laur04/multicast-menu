import celery
import os
import psutil
import signal

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from ..add.models import ManualReport, StreamSubmission
from ..add.tasks import verify_manual_report


# Allows an authenticated user to view all of the streams that they have submitted through the platform
@login_required
def manage_index(request):
    context = {
        "streams": StreamSubmission.objects.filter(owner=request.user),
        "reports": ManualReport.objects.filter(owner=request.user),
    }

    return render(request, "manage/index.html", context=context)


# Allows an authenticated user to stop a stream
@login_required
def stop_stream(request, submission_id):
    submission = get_object_or_404(StreamSubmission, id=submission_id)

    children = psutil.Process(submission.task_pid).children(recursive=True)
    os.killpg(submission.task_pid, signal.SIGKILL)
    for child in children:
        try:
            child.kill()
        except psutil.NoSuchProcess:
            pass
    celery.task.control.revoke(submission.celery_task_id, terminate=True)

    return redirect(reverse("manage:manage_index"))


# Allows an authenticated user to retry verifying a manual report
@login_required
def retry_verification(request, report_id):
    report = get_object_or_404(ManualReport, id=report_id)
    verify_manual_report.delay(report.id)

    return redirect(reverse("manage:manage_index"))
