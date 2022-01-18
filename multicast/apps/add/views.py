from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay
from asgiref.sync import async_to_sync
import asyncio
from av import VideoFrame
import cv2
import json
import logging
import os
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from ...utils import create_random_file_path
from ..view.models import Stream
from .forms import AddByFileForm, AddByLiveForm, AddByManualForm
from .models import StreamSubmission
from .tasks import submit_file_to_translator, submit_live_to_translator, verify_manual_report


# Set up for WebRTC server
pcs = set()
relay = MediaRelay()

# Index page for add where an authenticated user can select how they would like to add a stream
@login_required
def add_index(request):
    return render(request, "add/add_index.html")


# Allows an authenticated user to upload a file to be streamed
@login_required
def add_stream_file(request):
    form = AddByFileForm()
    if request.method == "POST":
        form = AddByFileForm(request.POST, request.FILES)
        if form.is_valid():
            random_path = "{}/{}".format(settings.MEDIA_ROOT, create_random_file_path())
            fs = FileSystemStorage()
            fs.save(random_path, form.cleaned_data["file_to_stream"])
            ss = StreamSubmission.objects.create(
                owner = request.user,
                path_to_uploaded_file = random_path,
            )
            result = submit_file_to_translator.delay(ss.id)
            ss.celery_task_id = result.id
            ss.save()
            return redirect(reverse("manage:manage_index"))

    return render(request, "add/add_file.html", context={"form": form})


# Allows an authenticated user to stream a live video
@login_required
def add_stream_live(request):
    form = AddByLiveForm()
    return render(request, "add/add_live.html", context={"form": form})


# Allows an authenticated user to manually report a stream
@login_required
def add_stream_manual(request):
    form = AddByManualForm()
    if request.method == "POST":
        form = AddByManualForm(request.POST)
        if form.is_valid():
            report = form.save()
            report.owner = request.user
            report.save()
            result = verify_manual_report.delay(report.id)
            report.celery_task_id = result.id
            report.save()
            return redirect(reverse("manage:manage_index"))
    
    return render(request, "add/add_manual.html", context={"form": form})


# WebRTC server
ROOT = os.path.dirname(__file__)

logger = logging.getLogger("pc")
pcs = set()
relay = MediaRelay()


class VideoTransformTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from an another track.
    """

    kind = "video"

    def __init__(self, track, transform):
        super().__init__()  # don't forget this!
        self.track = track
        self.transform = transform

    async def recv(self):
        frame = await self.track.recv()

        if self.transform == "cartoon":
            img = frame.to_ndarray(format="bgr24")

            # prepare color
            img_color = cv2.pyrDown(cv2.pyrDown(img))
            for _ in range(6):
                img_color = cv2.bilateralFilter(img_color, 9, 9, 7)
            img_color = cv2.pyrUp(cv2.pyrUp(img_color))

            # prepare edges
            img_edges = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            img_edges = cv2.adaptiveThreshold(
                cv2.medianBlur(img_edges, 7),
                255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY,
                9,
                2,
            )
            img_edges = cv2.cvtColor(img_edges, cv2.COLOR_GRAY2RGB)

            # combine color and edges
            img = cv2.bitwise_and(img_color, img_edges)

            # rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            return new_frame
        elif self.transform == "edges":
            # perform edge detection
            img = frame.to_ndarray(format="bgr24")
            img = cv2.cvtColor(cv2.Canny(img, 100, 200), cv2.COLOR_GRAY2BGR)

            # rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            return new_frame
        elif self.transform == "rotate":
            # rotate image
            img = frame.to_ndarray(format="bgr24")
            rows, cols, _ = img.shape
            M = cv2.getRotationMatrix2D((cols / 2, rows / 2), frame.time * 45, 1)
            img = cv2.warpAffine(img, M, (cols, rows))

            # rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            return new_frame
        else:
            return frame


@csrf_exempt
@async_to_sync
async def offer(request):
    params = await json.loads(request.body.decode())
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pcs.add(pc)

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    log_info("Created for %s", request.remote)

    # prepare local media
    player = MediaPlayer(os.path.join(ROOT, "demo-instruct.wav"))
    if args.record_to:
        recorder = MediaRecorder(args.record_to)
    else:
        recorder = MediaBlackhole()

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info("Connection state is %s", pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)

        if track.kind == "audio":
            pc.addTrack(player.audio)
            recorder.addTrack(track)
        elif track.kind == "video":
            pc.addTrack(
                VideoTransformTrack(
                    relay.subscribe(track), transform=params["video_transform"]
                )
            )
            if args.record_to:
                recorder.addTrack(relay.subscribe(track))

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)
            await recorder.stop()

    # handle offer
    await pc.setRemoteDescription(offer)
    await recorder.start()

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return HttpResponse(
        json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
        content_type="application/json",
    )


@async_to_sync
async def on_shutdown(request):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
