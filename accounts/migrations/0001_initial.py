# Generated by Django 4.2.20 on 2025-03-28 08:15

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("slug", models.SlugField(blank=True, editable=False, unique=True)),
                ("email", models.EmailField(max_length=255, unique=True)),
                ("name", models.CharField(max_length=200)),
                ("is_admin", models.BooleanField(default=False, editable=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "image",
                    models.ImageField(blank=True, null=True, upload_to="profile_pics/"),
                ),
                ("last_verified_identity", models.DateTimeField(null=True)),
                ("login_method", models.CharField(max_length=50, null=True)),
            ],
            options={
                "db_table": "tbl_user_auth",
            },
        ),
    ]
