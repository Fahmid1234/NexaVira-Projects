from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from clients.models import Client
from projects.models import Project


class Command(BaseCommand):
    help = "Seed sample CEO user, clients and projects for local development."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="ceo")
        parser.add_argument("--password", default="ceo12345")
        parser.add_argument("--reset", action="store_true")

    def handle(self, *args, **options):
        # Ensure this command is safe for repeated runs (idempotent).
        if options["reset"]:
            Project.objects.all().delete()
            Client.objects.all().delete()

        User = get_user_model()
        username = options["username"]
        password = options["password"]

        ceo, created = User.objects.get_or_create(
            username=username,
            defaults={"is_staff": True, "is_superuser": True, "is_active": True},
        )
        if created:
            ceo.set_password(password)
            ceo.save(update_fields=["password"])
            self.stdout.write(self.style.SUCCESS(f"Created CEO user: {username} / {password}"))
        else:
            self.stdout.write(self.style.WARNING(f"CEO user already exists: {username}"))

        c1, _ = Client.objects.get_or_create(
            name="Apex Traders",
            defaults={"phone": "15551234567", "messenger_username": "apex.traders"},
        )
        c2, _ = Client.objects.get_or_create(
            name="BlueSky Logistics",
            defaults={"phone": "15557654321", "messenger_username": "bluesky.logistics"},
        )
        c3, _ = Client.objects.get_or_create(
            name="Cedar Studio",
            defaults={"phone": "15559876543", "messenger_username": "cedar.studio"},
        )

        today = date.today()
        samples = [
            (c1, "Inventory System", Decimal("2500.00"), today - timedelta(days=10), today + timedelta(days=20), Project.Status.ACTIVE),
            (c2, "Company Website Revamp", Decimal("1800.00"), today - timedelta(days=25), today - timedelta(days=2), Project.Status.ACTIVE),
            (c3, "Mobile App MVP", Decimal("4500.00"), today - timedelta(days=60), today + timedelta(days=5), Project.Status.ACTIVE),
            (c1, "SEO Optimization", Decimal("600.00"), today - timedelta(days=30), today - timedelta(days=5), Project.Status.COMPLETED),
        ]

        created_count = 0
        for client, title, budget, start_date, deadline, status in samples:
            _, was_created = Project.objects.get_or_create(
                client=client,
                title=title,
                defaults={
                    "budget": budget,
                    "start_date": start_date,
                    "deadline": deadline,
                    "status": status,
                },
            )
            created_count += 1 if was_created else 0

        self.stdout.write(self.style.SUCCESS(f"Seed complete. New projects created: {created_count}"))

