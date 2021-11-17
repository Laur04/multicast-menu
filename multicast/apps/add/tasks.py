import os

from celery import current_task, shared_task


# Streams the file out to the translator
@shared_task
def submit_file_to_translator(submission):
    submission.celery_task_id = current_task.task_id
    submission.active = True
    submission.save()

    cmd = "/snap/bin/vlc {} --sout=udp://162.250.138.11:9001 --loop --sout-keep".format(submission.path_to_uploaded_file)
    os.system(cmd)


# Recieves the live content from the URL and streams it out to the translator
@shared_task
def submit_link_to_translator(submission):
    submission.celery_task_id = current_task.task_id
    submission.active = True
    submission.save()

    cmd = "/snap/bin/vlc {} --sout=udp://162.250.138.11:9001 --loop --sout-keep".format(submission.path_to_uploaded_file)
    os.system(cmd)


# Verifies the stream being reported before adding it
@shared_task
def verify_manual_report(report):
    report.celery_task_id = current_task.task_id
    report.active = True
    report.save()
