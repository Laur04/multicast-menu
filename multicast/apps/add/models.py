from django.contrib.auth import get_user_model
from django.db import models


# Submission to be streamed out to the translator
class StreamSubmission(models.Model):
    id = models.AutoField(primary_key=True)

    # Ownership information - required
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="stream_submission_set")
    time_submitted = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    # Source information - one is required
    path_to_uploaded_file = models.CharField(max_length=100, blank=True, null=False)
    url_to_streamed_video = models.URLField(blank=True, null=True)

    # Celery information - required
    celery_task_id = models.CharField(max_length=50)
    active = models.BooleanField(default=False)
    task_pid = models.CharField(max_length=50)

    # Pretty string output of a StreamSubmission
    def __str__(self):
        return "Submission {} ({})".format(self.id, self.celery_task_id)


# Report of a stream that needs to be verified
class ManualReport(models.Model):
    id = models.AutoField(primary_key=True)

    # Ownership information - required
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="manual_report_set")
    time_submitted = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    # Status information - required
    verified = models.BooleanField(default=False, blank=False, null=False)

    # Source information - required
    source = models.CharField(max_length=50, blank=False, null=False)
    group = models.CharField(max_length=50, blank=False, null=False)
    udp_port = models.CharField(max_length=50, blank=False, null=False)

    # Celery information - required
    celery_task_id = models.CharField(max_length=50)
    active = models.BooleanField(default=False)

    # Pretty string output of a ManualReport
    def __str__(self):
        return "Report {} ({})".format(self.id, self.celery_task_id)
