from django.contrib.auth.models import AbstractUser

from authentication.constants import ADMINISTRATOR

__all__ = [
    "User",
]


class User(AbstractUser):
    def __str__(self):
        return self.username

    def get_admin_group(self):
        groups = self.groups.filter(name=ADMINISTRATOR)  # name isn't unique!
        return groups.last() if groups.count() == 1 else None
