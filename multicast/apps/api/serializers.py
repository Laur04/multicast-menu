from rest_framework import serializers


# Serialize TranslationServerSubmission
class SubmissionSerializer(serializers.Serializer):
    unique_identifier = serializers.CharField(max_length=100)
    source = serializers.CharField(max_length=50)
    group = serializers.CharField(max_length=50)
    access_code = serializers.CharField(max_length=50)
