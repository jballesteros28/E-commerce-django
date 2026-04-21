from __future__ import annotations

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea o actualiza un superusuario por defecto."

    def handle(self, *args, **options) -> None:
        User = get_user_model()

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not email or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Faltan variables de entorno para crear el superusuario."
                )
            )
            return

        user = User.objects.filter(username=username).first()

        if user is None:
            user = User.objects.filter(email=email).first()

        if user is None:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superusuario '{username}' creado correctamente."
                )
            )
            return

        # Si ya existe, lo elevamos a admin real
        user.username = username
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Usuario '{username}' actualizado como superusuario."
            )
        )