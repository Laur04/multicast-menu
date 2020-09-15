from django.db import models

import datetime
import pytz

class M_Source(models.Model):
    ip = models.CharField(max_length=100)

    def __str__(self):
        return self.ip

class Stream(models.Model):
    whois = models.CharField(max_length=100)
    source = models.CharField(max_length=50)
    group = models.CharField(max_length=50)
    pps = models.IntegerField(blank=True, null=True)
    active = models.BooleanField(default=True)
    last_found = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(blank=True, null=True)
    downvote = models.IntegerField(default=0)

    def __str__(self):
        return 'amt://' + self.source + '@' + self.group

    def get_s_g(self):
        return self.source + '_' + self.group

    def older_than_seven(self):
        utc = pytz.UTC
        diff = datetime.datetime.today() - datetime.timedelta(days=7)
        diff = utc.localize(diff)
        if self.last_found < diff:
            return True
        return False

class Description(models.Model):
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE) 
    description = models.CharField(max_length=10000)
    votes = models.IntegerField(default=0)

    def upvote(self):
        self.votes += 1
        self.save()

    def __str__(self):
        return self.description