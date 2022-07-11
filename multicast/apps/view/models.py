from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Stream(models.Model):
    id = models.AutoField(primary_key=True)

    COLLECTION_METHODS = (("01", "Scraping"), ("02", "Manual"), ("03", "Upload"), ("04", "API"))

    # Administrative
    active = models.BooleanField(default=True)
    collection_method = models.CharField(max_length=2, choices=COLLECTION_METHODS, null=True, blank=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)

    # Stream
    amt_relay = models.CharField(max_length=100, null=True, blank=True)
    group = models.GenericIPAddressField(null=True, blank=True)
    source = models.GenericIPAddressField(null=True, blank=True)
    udp_port = models.IntegerField(null=True, blank=True)

    # Display
    categories = models.ManyToManyField(Category)
    description = models.CharField(max_length=100, null=True, blank=True)
    report_count = models.IntegerField(default=0)
    source_name = models.CharField(max_length=100, null=True, blank=True)
    thumbnail = models.ImageField(null=True, blank=True, upload_to="stream_previews/%Y/%m/%d/%H")
    preview = models.ImageField(null=True, blank=True, upload_to="stream_previews/%Y/%m/%d/%H")
    editors_choice = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name="liked_streams")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} (Source: {}, Group: {})".format(self.get_description(), self.source, self.group)

    # Returns the owner's description, if set, otherwise returns the most popular user description
    def get_description(self):
        if self.description:
            return self.description
        elif self.user_description_set.all():
            return self.user_description_set.order_by("-votes")[0]
        else:
            return "No description available"

    # Returns the last time this stream's collection object was updated
    def get_time_last_found(self):
        if self.collection_method == "01":
            return self.scraping.time
        elif self.collection_method == "02":
            return self.manual.time
        elif self.collection_method == "03":
            return self.upload.time
        elif self.collection_method == "04":
            return self.api.time
        return None

    # Updates the "time" field on this stream's collection object
    def update_last_found(self):
        new_time = timezone.now()
        if self.collection_method == "01":
            self.scraping.time = new_time
            self.scraping.save()
        elif self.collection_method == "02":
            self.manual.time = new_time
            self.manual.save()
        elif self.collection_method == "03":
            self.upload.time = new_time
            self.upload.save()
        elif self.collection_method == "04":
            self.api.time = new_time
            self.api.save()

    # Allow users to report broken streams
    def report(self):
        self.report_count += 1
        if self.report_count > 10:
            self.active = False
        self.save()

    # Returns the URL address of the stream
    def get_url(self):
        url = "amt://" + self.source + "@" + self.group
        if self.udp_port:
            url = url + ":" + str(self.udp_port)
        return url


class Description(models.Model):
    id = models.AutoField(primary_key=True)

    # Administration
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name="user_description_set")
    user_submitted = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    # Display
    text = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return "{}".format(self.text)

    # Increase the count of votes
    def upvote(self):
        self.votes += 1
        self.save()

    # Decrease the count of votes
    def downvote(self):
        self.votes -= 1
        self.save()
