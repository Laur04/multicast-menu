from celery import shared_task
import subprocess

from django.core import management

from ..view.models import Stream
from .models import ManualReport, StreamSubmission


# Streams the file out to the translator
@shared_task
def submit_file_to_translator(submission_id):
    submission = StreamSubmission.objects.get(id=submission_id)
    submission.active = True
    submission.save()

    proc = subprocess.Popen(["/usr/bin/sudo", "-u", "web", "/usr/bin/vlc", submission.path_to_uploaded_file, "--sout=udp://162.250.138.11:9001", "--loop", "--sout-keep"])
    submission.task_pid = proc.pid
    submission.save()


# Verifies the stream being reported before adding it
@shared_task
def verify_manual_report(report_id):
    report = ManualReport.objects.get(id=report_id)
    report.active = True
    report.save()

    if Stream.objects.filter(source=report.source, group=report.group).exists():
        report.verified = False
        report.error_message = "That stream already exists."
    else:
        try:
            stream = Stream.objects.create(
                owner = report.owner,
                submission_method = "2",
                source = report.source,
                group = report.group,
                udp_port = report.udp_port,
                owner_whois = report.owner_whois,
                owner_description = report.owner_description,
            )
            if report.amt_gateway:
                stream.amt_gateway = report.amt_gateway
                stream.save()
            stream.set_whois()

            report.verified = True
            report.error_message = "No errors"
            report.stream = stream
        except:
            report.verified = False
            report.error_message = "Unexpected error in verifying report."

    report.active = False
    report.save()


# Scrapes Internet2 and GEANT for active streams
@shared_task
def scrape_for_streams():
    management.call_command("scrape_streams")
