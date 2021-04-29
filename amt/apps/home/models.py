import datetime
import ipwhois
import pytz

from django.db import models


class M_Source(models.Model):
    ip = models.CharField(max_length=100)

    def __str__(self):
        return self.ip


class Stream(models.Model):
    whois = models.CharField(max_length=100)
    source = models.CharField(max_length=50)
    udp_port = models.CharField(max_length=50, blank=True, null=True)
    group = models.CharField(max_length=50)
    pps = models.IntegerField(blank=True, null=True)
    active = models.BooleanField(default=True)
    last_found = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(blank=True, null=True)
    downvote = models.IntegerField(default=0)

    def __str__(self):
        title = self.description_set.order_by("-votes")[0] if self.description_set else "No title available"
        return "{} (Source: {}, Group: {})".format(title, self.source, self.group)

    def get_s_g(self):
        return self.source + '_' + self.group

    def save(self, *args, **kwargs):
        info = ipwhois.IPWhois(self.source).lookup_rdap()
        asn_desc = info['asn_description']
        desc = info['network']['remarks'][0]['description'] if info['network']['remarks'] is not None else None
        who_is = asn_desc if asn_desc is not None else desc
                
        super(Stream, self).save(*args, **kwargs)


class Description(models.Model):
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE) 
    description = models.CharField(max_length=10000)
    votes = models.IntegerField(default=0)

    def upvote(self):
        self.votes += 1
        self.save()

    def __str__(self):
        return self.description
