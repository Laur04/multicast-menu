from celery import shared_task
import os
from scapy.all import Packet, send
from scapy.contrib.igmpv3 import IGMPv3, IGMPv3gr, IGMPv3mr
from scapy.layers.inet import IP, UDP
import secrets
import socket
import struct
import subprocess
import tempfile

from django.core.files import File
from django.shortcuts import get_object_or_404

from ...settings import MEDIA_ROOT
from .amt.constants import DEFAULT_MTU, LOCAL_LOOPBACK, MCAST_ALLHOSTS, MCAST_ANYCAST
from .amt.models import (
    AMT_Discovery,
    AMT_Relay_Request,
    AMT_Membership_Query,
    AMT_Membership_Update,
    AMT_Multicast_Data,
)
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
    amt_port = tunnel.get_amt_port_number()
    udp_port = tunnel.get_udp_port_number()
    
    # Set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    s.bind(('', amt_port))

    # Configure IP and UDP layers
    ip_top_layer = IP(dst=relay)
    udp_top_layer = UDP(sport=amt_port, dport=2268)    
    nonce = secrets.token_bytes(4)

    # Send AMT relay discovery
    amt_layer = AMT_Discovery()
    amt_layer.setfieldval("nonce", nonce)
    send(ip_top_layer / udp_top_layer / amt_layer)
    data, _ = s.recvfrom(DEFAULT_MTU)

    # Send AMT relay advertisement
    amt_layer = AMT_Relay_Request()
    amt_layer.setfieldval("nonce", nonce)
    send(ip_top_layer / udp_top_layer / amt_layer)
    data, _ = s.recvfrom(DEFAULT_MTU)

    # Send AMT multicast membership query
    membership_query = AMT_Membership_Query(data)
    response_mac = membership_query.response_mac
    req = struct.pack("=4sl", socket.inet_aton(multicast), socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, req)

    amt_layer = AMT_Membership_Update()
    amt_layer.setfieldval("nonce", nonce)
    amt_layer.setfieldval("response_mac", response_mac)

    options_pkt = Packet(b"\x00")
    ip_layer2 = IP(src=MCAST_ANYCAST, dst=MCAST_ALLHOSTS, options=[options_pkt])

    igmp_layer = IGMPv3()
    igmp_layer.type = 34

    igmp_layer2 = IGMPv3mr(records=[IGMPv3gr(maddr=multicast, srcaddrs=[source])])

    send(ip_top_layer / udp_top_layer / amt_layer / ip_layer2 / igmp_layer / igmp_layer2)

    tunnel.amt_gateway_up = True
    tunnel.save()

    # Loop for data
    count = 0
    notified = False
    while True:
        data, _ = s.recvfrom(DEFAULT_MTU)

        try: 
            amt_packet = AMT_Multicast_Data(data)
            raw_udp = bytes(amt_packet[UDP].payload)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.sendto(raw_udp, (LOCAL_LOOPBACK, udp_port))
        except Exception as err:
            print(f"Error occurred in processing packet {err}")

        if count < 50:
            print(".", flush=True, end="")
            count += 1
        else:
            if not notified:
                notified = True


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
    ])
    
    tunnel.ffmpeg_pid = proc.pid
    tunnel.save()

    tunnel.ffmpeg_up = True
    tunnel.save()
