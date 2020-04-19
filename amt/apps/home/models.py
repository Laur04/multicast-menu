from django.db import models

class M_Source(models.Model):
    ip = models.CharField(max_length=100)

    def __str__(self):
        return self.ip
