from django.contrib.auth import get_user_model
from django.db import models

from ..view.models import Stream


# Submission to be streamed out to the translator
class StreamSubmission(models.Model):
    id = models.AutoField(primary_key=True)

    stream = models.OneToOneField(Stream, on_delete=models.SET_NULL, null=True)

    # Ownership information - required
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="stream_submission_set")
    time_submitted = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    # Source information - required
    path_to_uploaded_file = models.CharField(max_length=100, blank=True, null=False)

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

    stream = models.OneToOneField(Stream, on_delete=models.SET_NULL, null=True)

    # Ownership information - required
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="manual_report_set", null=True)
    time_submitted = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    # Status information - verified required
    verified = models.BooleanField(default=False, blank=False, null=False)
    error_message = models.CharField(max_length=100, blank=True, null=True)

    # Source information - required except udp_port
    source = models.CharField(max_length=50, blank=False, null=False)
    group = models.CharField(max_length=50, blank=False, null=False)
    udp_port = models.CharField(max_length=50, blank=True, null=True)
    amt_gateway = models.CharField(max_length=100, blank=True, null=True)

    # Metadata - required
    owner_whois = models.CharField(max_length=100, blank=True, null=True)
    owner_description = models.CharField(max_length=10000, blank=True, null=True)

    # Celery information - required
    celery_task_id = models.CharField(max_length=50)
    active = models.BooleanField(default=False)

    # Pretty string output of a ManualReport
    def __str__(self):
        return "Report of {}@{}".format(self.source, self.group)


# Record of queries that fail in the automated scraping process
class FailedQuery(models.Model):
    id = models.AutoField(primary_key=True)

    # The time the failed query was executed
    time_failed = models.DateTimeField(auto_now_add=True)

    # The IP that the failed query was attempting to reach
    ip = models.CharField(max_length=100, blank=False, null=False)

    # Pretty string output of a FailedQuery
    def __str__(self):
        return "Failed on {} at {}".format(self.ip, self.time_failed)
