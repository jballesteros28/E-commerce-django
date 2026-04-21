from __future__ import annotations

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea un superusuario por defecto si no existe."

    def handle(self, *args, **options) -> None:
        User = get_user_model()

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "No se creó el superusuario: faltan variables de entorno "
                    "DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL o "
                    "DJANGO_SUPERUSER_PASSWORD."
                )
            )
            return

        user_exists = User.objects.filter(username=username).exists()
        email_exists = User.objects.filter(email=email).exists()

        if user_exists or email_exists:
            self.stdout.write(
                self.style.SUCCESS(
                    "El superusuario ya existe. No se creó uno nuevo."
                )
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Superusuario '{username}' creado correctamente."
            )
        )