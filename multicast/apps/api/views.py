from rest_framework import generics, status
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from ...utils import create_random_file_path
from ..view.models import Stream
from .models import TranslationServer, TranslationServerSubmission
from .serializers import SubmissionSerializer


class SubmissionAdd(generics.CreateAPIView):
    serializer_class = SubmissionSerializer
    queryset = TranslationServerSubmission.objects.all()

    def get_queryset(self):
        return TranslationServerSubmission.objects.all()

    def create(self, request):
        try:
            source = request.data.get("source")
            group = request.data.get("group")
            unique_identifier = request.data.get("unique_identifier")
        except:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                translation_server = TranslationServer.objects.get(unique_identifier=unique_identifier)
            except:
                return Response({"error": "Invalid translation server unique identifier"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                access_code = create_random_file_path() + create_random_file_path()

                submission = TranslationServerSubmission.objects.create(
                    translation_server = translation_server,
                    source = source,
                    group = group,
                    access_code = access_code,
                )

                owner = get_user_model().objects.get_or_create(get_user_model(), username=submission.translation_server.nice_name)
                Stream.objects.create(
                    owner = owner,
                    submission_method = "3",
                    source = submission.source,
                    group = submission.group,
                    access_code = access_code,
                )

                return Response({"data": "Your access code for claiming, editing or deleting the string is {}".format(access_code)}, status=status.HTTP_201_CREATED)


class SubmissionRemove(generics.CreateAPIView):
    serializer_class = SubmissionSerializer
    queryset = TranslationServerSubmission.objects.all()

    def get_queryset(self):
        return TranslationServerSubmission.objects.all()

    def create(self, request):
        try:
            access_code = request.data.get("access_code")
        except:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                submission = TranslationServerSubmission.objects.get(access_code=access_code)
                stream = Stream.objects.get(access_code=access_code)
            except:
                return Response({"error": "Invalid submission access code."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                submission.delete()
                stream.delete()

                return Response({"data": "Your stream has been deleted."}, status=status.HTTP_201_CREATED)    
