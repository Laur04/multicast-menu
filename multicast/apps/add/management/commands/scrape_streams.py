from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from ....view.models import Stream
from ...models import FailedQuery, ScrapingSubmission
from .run import run


class Command(BaseCommand):
    help = "Scrape the looking glasses and import streams onto the site."

    def handle(self, *args, **kwargs):
        results_dict, failure = run()

        scrape_user = get_user_model().objects.get_or_create(
            username="SCRAPER"
        )[0]

        print(results_dict)

        for results in results_dict:
            filtered_streams = Stream.objects.filter(source=results["source"], group=results["group"])
            if not filtered_streams.exists():
                stream = Stream.objects.create(
                    owner=scrape_user,
                    collection_method="01",
                    source=results["source"], 
                    group=results["group"],
                    source_name=results["status"],
                )
                ScrapingSubmission.objects.create(stream=stream)
            else:
                try:
                    stream = filtered_streams.get(collection_method="01")
                except:
                    pass
                else:
                    stream.active = True
                    stream.save()
                    submission = ScrapingSubmission.objects.get(stream=stream)
                    submission.save()


        if failure:
            FailedQuery.objects.create(ip="8.8.8.8")
