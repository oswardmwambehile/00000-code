from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a user with an email and password."""
        if not email:
            raise ValueError("The Email field must be provided.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with all privileges."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not password:
            raise ValueError("Superusers must have a password.")
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


# -------------------
# Branch Model
# -------------------
class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name or "Unnamed Branch"


# -------------------
# User Model
# -------------------
class User(AbstractBaseUser, PermissionsMixin):
    POSITION_CHOICES = [
        ('Head of Sales', 'Head of Sales'),
        ('Facilitator', 'Facilitator'),
        ('Product Brand Manager', 'Product Brand Manager'),
        ('Corporate Manager', 'Corporate Manager'),
        ('Corporate Officer', 'Corporate Officer'),
        ('Zonal Sales Executive', 'Zonal Sales Executive'),
        ('Mobile Sales Officer', 'Mobile Sales Officer'),
        ('Desk Sales Officer', 'Desk Sales Officer'),
        ('Admin', 'Admin'),
    ]

    ZONE_CHOICES = [
        ('Coast Zone', 'Coast Zone'),
        ('Corporate', 'Corporate'),
        ('Central Zone', 'Central Zone'),
        ('Southern Zone', 'Southern Zone'),
        ('Northern Zone', 'Northern Zone'),
        ('Lake Zone', 'Lake Zone'),
    ]

    COMPANY_CHOICES = [
        ('ANDO', 'ANDO'),
        ('KAM', 'KAM'),
        ('MATE', 'MATE'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    company_name = models.CharField(max_length=50, choices=COMPANY_CHOICES, blank=True, null=True)
    position = models.CharField(max_length=100, choices=POSITION_CHOICES, blank=True, null=True)
    zone = models.CharField(max_length=100, choices=ZONE_CHOICES, blank=True, null=True)

    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    contact = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^(?:\+255|0)[67][0-9]\d{7}$',
                message="Enter a valid Tanzanian phone number (e.g. +255712345678 or 0712345678)"
            )
        ]
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    def get_short_name(self):
        return self.first_name or self.email
