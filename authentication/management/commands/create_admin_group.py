from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from authentication.constants import ADMINISTRATOR

__all__ = ["Command"]


class Command(BaseCommand):
    help = """Create "Administrator Group" and add Permissions"""

    def handle(self, *args, **options):
        admin_group, created = Group.objects.get_or_create(name=ADMINISTRATOR)
        if created:
            self._set_permissions(admin_group)

    @staticmethod
    def _set_permissions(admin_group):
        codenames = [
            "add_user",
            "change_user",
            "delete_user",
            "view_user",
            "add_product",
            "change_product",
            "delete_product",
            "view_product",
        ]
        permissions = Permission.objects.filter(codename__in=codenames)
        for permission in permissions:
            admin_group.permissions.add(permission)
        admin_group.save()
