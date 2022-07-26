import os
import tempfile

from celery import shared_task
from django.core.files import File

from multicast.apps.view.models import Stream
from multicast.apps.view.util.stream_preview import snapshot_multicast_stream, resize_image


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
