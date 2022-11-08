from celery import shared_task
import os
import subprocess
import tempfile

from django.core.files import File
from django.shortcuts import get_object_or_404

from ...settings import MEDIA_ROOT
from .amt.constants import LOCAL_LOOPBACK
from .models import Stream, Tunnel
from .util.stream_preview import snapshot_multicast_stream, resize_image


@shared_task
def create_preview_for_stream(stream_id):
    """
    Shared task that creates a thumbnail and a preview for a stream by a given stream ID.

    The task calls a script that connects to the stream and creates a couple of snapshots
    in a temporary directory. If the script was able to create any snapshots, one of them
    is chosen (currently the first one) and from it a thumbnail and a preview are created
    and then saved to the thumbnail and preview fields of the stream.

    :param stream_id:
    :return:
    """
    if stream_id is None:
        ValueError("Illegal argument: stream_id is null!")
    if not isinstance(stream_id, int):
        ValueError("Illegal argument: stream_id is not an integer!")

    # Get the stream object
    stream = Stream.objects.get(id=stream_id)
    # Create a temp directory
    temp_dir = tempfile.TemporaryDirectory()
    # Snapshot the stream and save the images in the temp directory
    amt_relay = stream.amt_relay if stream.amt_relay is not None else "amt-relay.m2icast.net"
    snapshot_multicast_stream(stream.get_url(), amt_relay, temp_dir.name)
    # List the snapshots
    snapshots = os.listdir(temp_dir.name)
    # Check if there are any snapshots
    if snapshots:
        # Get one of the snapshots
        first_snapshot = snapshots[0]
        # Build the path to the snapshot
        str_snapshot_path = os.path.join(temp_dir.name, first_snapshot)

        # Create a temp file for the thumbnail
        with tempfile.NamedTemporaryFile() as thumbnail:
            # Resize the original snapshot and save it to the temp file
            resize_image(str_snapshot_path, thumbnail.name, i_width=440)
            # Get the stream again, so that we don't overwrite some data,
            # which might have changed while taking the snapshots
            stream = Stream.objects.get(id=stream_id)
            # Delete the old file without saving, because the field will be saved on the next line
            stream.thumbnail.delete(save=False)
            # Update the thumbnail in the stream object
            stream.thumbnail.save("stream_" + str(stream_id) + "_thb.jpg", File(thumbnail), save=True)

        # Create a temp file for the preview
        with tempfile.NamedTemporaryFile() as preview:
            # Resize the original snapshot and save it to the temp file
            resize_image(str_snapshot_path, preview.name, i_width=880)
            # Get the stream again, so that we don't overwrite some data,
            # which might have changed while taking the snapshots
            stream = Stream.objects.get(id=stream_id)
            # Delete the old file without saving, because the field will be saved on the next line
            stream.preview.delete(save=False)
            # Update the preview in the stream object
            stream.preview.save("stream_" + str(stream_id) + "_prw.jpg", File(preview), save=True)

    # Remove the temp directory
    temp_dir.cleanup()


@shared_task
def open_tunnel(tunnel_id):
    tunnel = get_object_or_404(Tunnel, id=tunnel_id)

    relay = tunnel.stream.amt_relay if tunnel.stream.amt_relay else "amt-relay.m2icast.net"
    source = tunnel.stream.source
    multicast = tunnel.stream.group
    amt_port = str(tunnel.get_amt_port_number())
    udp_port = str(tunnel.get_udp_port_number())

    proc = subprocess.Popen([
        "pipenv",
        "run",
        "python3",
        "/var/www/html/multicast/apps/view/amt/tunnel.py",
        relay,
        source,
        multicast,
        amt_port,
        udp_port
    ], shell=True, stdin=None, stderr=None)


    tunnel.amt_gateway_pid = proc.pid
    tunnel.amt_gateway_up = True
    tunnel.save()


@shared_task
def start_ffmpeg(tunnel_id):
    tunnel = get_object_or_404(Tunnel, id=tunnel_id)

    proc = subprocess.Popen([
        "ffmpeg",
        "-i",
        f"udp://{LOCAL_LOOPBACK}:{tunnel.get_udp_port_number()}",
        "-c",
        "copy",
        "-f",
        "hls",
        f"{MEDIA_ROOT}/tunnel-files/{tunnel.get_filename()}"
    ], shell=True, stdin=None, stderr=None)
    
    tunnel.ffmpeg_pid = proc.pid
    tunnel.ffmpeg_up = True
    tunnel.save()
