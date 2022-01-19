import ipwhois

from django.contrib.auth import get_user_model
from django.db import models


class Stream(models.Model):
    id = models.AutoField(primary_key=True)

    METHODS = (("1", "Scraping"), ("2", "Manual Report"), ("3", "File Submission"))

    # Ownership information - required
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="stream_set")

    # Submission information - required
    submission_method = models.CharField(max_length=5, choices=METHODS)

    # Stream specific information - source and group required
    whois = models.CharField(max_length=100, blank=True, null=True)
    pps = models.IntegerField(blank=True, null=True)
    source = models.CharField(max_length=50, blank=False, null=False)
    group = models.CharField(max_length=50, blank=False, null=False)
    udp_port = models.CharField(max_length=50, blank=True, null=True)
    amt_gateway = models.CharField(max_length=100, blank=True, null=True)

    # Activity information - required
    active = models.BooleanField(default=True, blank=False, null=False)
    last_found = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    report_count = models.IntegerField(default=0, blank=False, null=False)

    # Metadata provided by owner - not required
    owner_whois = models.CharField(max_length=100, blank=True, null=True)
    owner_description = models.CharField(max_length=10000, blank=True, null=True)

    # Pretty string version of stream information
    def __str__(self):
        title = self.description_set.order_by("-votes")[0] if len(self.description_set.all()) > 0 else "No title available"
        return "{} (Source: {}, Group: {})".format(title, self.source, self.group)

    # Query for WhoIs data based on source field
    def set_whois(self):
        info = ipwhois.IPWhois(self.source).lookup_rdap()
        asn_desc = info["asn_description"]
        desc = info["network"]["remarks"][0]["description"] if info["network"]["remarks"] is not None else None
        self.whois = asn_desc if asn_desc is not None else desc
        self.save()

    # Allow users to report broken streams
    def report(self):
        self.report_count += 1
        if self.report_count > 10:
            self.active = False
        self.save()


class Description(models.Model):
    id = models.AutoField(primary_key=True)

    # Ownership information - required
    user_submitted = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="description_set", blank=False, null=False)

    # Stream affiated with - required
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, blank=False, null=False)

    # Actual text of the description - required 
    description = models.CharField(max_length=10000, blank=False, null=False)

    # Upvotes of the descrition - required
    votes = models.IntegerField(default=0, blank=False, null=False)

    # Pretty string version of the description
    def __str__(self):
        short_description = self.description[10] + "..." if len(self.description) > 13 else self.description
        return "{} - {}".format(short_description, self.stream)

    # Increase the count of votes
    def upvote(self):
        self.votes += 1
        self.save()

    # Decrease the count of votes
    def downvote(self):
        self.votes -= 1
        self.save()
