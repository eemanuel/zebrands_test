from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from factory import Faker, PostGenerationMethodCall, django

from authentication.constants import ADMINISTRATOR
from authentication.management.commands.create_admin_group import Command as CreateAdminGroupCommand

User = get_user_model()


class UserFactory(django.DjangoModelFactory):
    username = Faker("user_name")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = Faker("email")
    password = PostGenerationMethodCall("set_password", "admin")

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, with_admin_group=False, *args, **kwargs):
        user = super()._create(model_class, *args, **kwargs)
        if with_admin_group:
            admin_group, created = Group.objects.get_or_create(name=ADMINISTRATOR)
            if created:
                CreateAdminGroupCommand._set_permissions(admin_group)
            user.groups.add(admin_group)
        return user
