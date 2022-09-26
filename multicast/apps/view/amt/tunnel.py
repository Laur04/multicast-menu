from scapy.all import Packet, send
from scapy.contrib.igmpv3 import IGMPv3, IGMPv3gr, IGMPv3mr
from scapy.layers.inet import IP, UDP
import secrets
import socket
import struct
import sys

from .constants import DEFAULT_MTU, LOCAL_LOOPBACK, MCAST_ALLHOSTS, MCAST_ANYCAST
from .models import (
    AMT_Discovery,
    AMT_Relay_Request,
    AMT_Membership_Query,
    AMT_Membership_Update,
    AMT_Multicast_Data,
)


relay = sys.argv[1]
source = sys.argv[2]
multicast = sys.argv[3]
amt_port = int(sys.argv[4])
udp_port = int(sys.argv[5])


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
