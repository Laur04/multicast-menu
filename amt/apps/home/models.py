from django.db import models

class M_Source(models.Model):
    ip = models.CharField(max_length=100)

    def __str__(self):
        return self.ip

class Stream(models.Model):
    whois = models.CharField(max_length=100)
    source = models.CharField(max_length=50)
    group = models.CharField(max_length=50)
    pps = models.IntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return 'amt://' + self.source + '@' + self.group

    def get_s_g(self):
        return self.source + '_' + self.group

class Description(models.Model):
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE) 
    votes = models.IntegerField(default=0)
