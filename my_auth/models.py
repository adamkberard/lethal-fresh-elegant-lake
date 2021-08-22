import uuid as uuid_lib

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager

# Changing from the standard django user to my own custom user. This is advantageous
# because changing from the standard django user to a custom user later in the project's
# life can be quite difficult so I just do it at the beginning. I also like to user emails
# to log people in rather than usernames so that's the main reason.
class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    
    uuid = models.UUIDField(
        db_index=True,
        default=uuid_lib.uuid4,
        editable=False,
        primary_key=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
