from django.db import models


# Model to represent available translation server
class TranslationServer(models.Model):
    id = models.AutoField(primary_key=True)

    # The name that the server will call itself when communicating to the API - required
    unique_identifier = models.CharField(max_length=100, blank=False, null=False)
    
    # A nice name that will be shown to platform users - required
    nice_name = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return "{} ({})".format(self.nice_name, self.unique_identifier)


# Model to recieve translation server information
class TranslationServerSubmission(models.Model):
    id = models.AutoField(primary_key=True)

    translation_server = models.ForeignKey(TranslationServer, on_delete=models.SET_NULL)

    source = models.CharField(max_length=50, blank=False, null=False)
    group = models.CharField(max_length=50, blank=False, null=False)

    # Used to control access to stream that is submitted.
    access_code = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return "{}@{} from {}".format(self.source, self.group, self.translation_server)
