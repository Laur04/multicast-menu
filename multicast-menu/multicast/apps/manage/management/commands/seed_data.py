from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
import random

from ....view.models import (
    Category,
    Stream,
    Description,
    TrendingStream,
)

from ....add.models import ManualSubmission


User = get_user_model()

class Command(BaseCommand):
    help = "Seed database with fake data"

    @transaction.atomic
    def handle(self, *args, **kwargs):

        if User.objects.filter(username="admin").exists():
            self.stdout.write(self.style.SUCCESS("Data already seeded"))
            return

        # --------------------------------------------------
        # SUPERUSER
        # --------------------------------------------------
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123",
        )

        # --------------------------------------------------
        # NORMAL USERS
        # --------------------------------------------------
        users = []
        for i in range(5):
            user = User.objects.create_user(
                username=f"user{i}",
                password="password123",
            )
            users.append(user)

        # --------------------------------------------------
        # CATEGORIES
        # --------------------------------------------------
        categories = []
        for name in ["Sports", "News", "Movies", "Gaming"]:
            categories.append(
                Category.objects.create(
                    name=name,
                    slug=name.lower()
                )
            )

        # --------------------------------------------------
        # STREAMS
        # --------------------------------------------------
        streams = []

        for i in range(10):
            stream = Stream.objects.create(
                active=True,
                collection_method="02",
                owner=random.choice(users),
                group="239.0.0.{}".format(i + 1),
                source="192.168.1.{}".format(i + 1),
                udp_port=5000 + i,
                description=f"Demo Stream {i}",
                source_name=f"Source {i}",
            )

            stream.categories.set(random.sample(categories, k=2))
            streams.append(stream)

            # Add submission object
            ManualSubmission.objects.create(
                stream=stream,
                active=True,
                error_msg="",
            )
                
            # Add descriptions
            for u in users:
                Description.objects.create(
                    stream=stream,
                    user_submitted=u,
                    text=f"Description from {u.username}",
                    votes=random.randint(0, 20),
                )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully"))
