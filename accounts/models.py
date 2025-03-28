import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import string
import random


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, password2=None):
        """
        Creates and saves a User with the given email, name, tc and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email), name=name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        """
        Creates and saves a superuser with the given email, name, tc and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


def generate_unique_slug(length=8):
    characters = string.ascii_uppercase + string.digits  # Uppercase letters and digits
    return ''.join(random.choices(characters, k=length))


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, blank=True, editable=False)

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=200)

    is_admin = models.BooleanField(default=False, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    # google or local
    last_verified_identity = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True
    )

    login_method = models.CharField(max_length=50, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"  # by default required
    REQUIRED_FIELDS = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:  # Generate slug only if it doesn't exist
            unique_slug = generate_unique_slug()
            while User.objects.filter(slug=unique_slug).exists():  # Ensure uniqueness
                unique_slug = generate_unique_slug()
            self.slug = unique_slug
        super().save(*args, **kwargs)

    class Meta:
        db_table = "tbl_user_auth"
