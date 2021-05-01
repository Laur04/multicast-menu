import re

from django.core.management.base import BaseCommand

from ...models import M_Source, Stream
from ...stream_collection.run_geant import run as run_geant
from ...stream_collection.run_i2 import run as run_i2


class Command(BaseCommand):
    help = "Scrape the looking glasses and import streams onto the site."

    def handle(self, *args, **kwargs):
        streams = set()
        streams.update(run_geant([s.ip for s in M_Source.objects.filter(looking_glass="GEANT")]))
        streams.update(run_i2([s.ip for s in M_Source.objects.filter(looking_glass="I2")]))

        for s in streams:  # s = (source, group, whois, pps)
            if re.match("^[0-9.]+$", s[0]) and s[0] != '193.17.9.3' and s[3] > 100:  # filter out IPv6, Eumsat, low PPS
                s = Stream.objects.update_or_create(source=s[0], group=s[1], defaults={"whois": s[2], "pps": s[3]})[0]
                print(s)

        print("Finished")
