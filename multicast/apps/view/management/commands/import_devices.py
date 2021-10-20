from django.core.management.base import BaseCommand, CommandError

from ...models import M_Source


class Command(BaseCommand):
    help = "Import devices as M_Sources from text file."

    def add_arguments(self, parser):
        parser.add_argument("path_to_data")
        parser.add_argument("looking_glass")

    def handle(self, *args, **kwargs):
        try:
            f_obj = open(kwargs["path_to_data"], "r")
        except OSError as ex:
            raise CommandError(str(ex)) from ex

        for d in f_obj.readlines():
            M_Source.objects.get_or_create(ip=d.strip(), looking_glass=kwargs["looking_glass"])

        print("Finished")
