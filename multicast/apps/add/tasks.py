import subprocess

from celery import shared_task

from .models import ManualReport, StreamSubmission


# Streams the file out to the translator
@shared_task
def submit_file_to_translator(submission_id):
    submission = StreamSubmission.objects.get(id=submission_id)
    submission.active = True
    submission.save()

    proc = subprocess.Popen(["/usr/bin/sudo -u web /usr/bin/vlc {} --sout=udp://162.250.138.11:9001 --loop --sout-keep".format(submission.path_to_uploaded_file)], shell=False)
    submission.task_pid = proc.pid
    submission.save()


# Recieves the live content from the URL and streams it out to the translator
@shared_task
def submit_link_to_translator(submission_id):
    submission = StreamSubmission.objects.get(id=submission_id)
    submission.active = True
    submission.save()

    proc = subprocess.Popen(["/usr/bin/sudo -u web /usr/bin/vlc {} --sout=udp://162.250.138.11:9001 --loop --sout-keep".format(submission.path_to_uploaded_file)], shell=False)
    submission.task_pid = proc.pid
    submission.save()


# Verifies the stream being reported before adding it
@shared_task
def verify_manual_report(report_id):
    report = ManualReport.objects.get(id=report_id)
    report.active = True
    report.save()
