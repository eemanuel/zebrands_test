from django.conf import settings

from rest_framework.viewsets import ModelViewSet

from authentication.permissions import CanCRUDProductPermission
from products.models import Product
from products.serializers import ProductSerializer

from utils.email import send_email

__all__ = [
    "ProductModelViewSet",
]


class ProductModelViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [
        CanCRUDProductPermission,
    ]

    def get_serializer(self, *args, **kwargs):
        """
        First obtain the serializer instance calling super().get_serializer
        Call Product.add_to_anonymous_queries_count only when user is AnonymousUser and action is "list" or "retrieve".
        This is here and not in "list" or "retrieve" methods
        to avoid call self.get_queryset multiple times (It evaluate multiple querys)
        """
        serilizer = super().get_serializer(*args, **kwargs)
        if self.request.user.is_anonymous and self.action in ("list", "retrieve"):
            instance_or_queryset = args[0]
            Product.add_to_anonymous_queries_count(instance_or_queryset, 1)
        return serilizer

    def perform_create(self, serializer):
        serializer.save()
        self._try_send_email_to_admins(serializer.data, "create")

    def perform_update(self, serializer):
        original_fields = serializer.instance.__dict__.copy()
        serializer.save()
        self._try_send_email_to_admins(original_fields, "update", serializer.data)

    def perform_destroy(self, instance):
        original_fields = instance.__dict__.copy()
        instance.delete()
        self._try_send_email_to_admins(original_fields, "destroy")

    def _try_send_email_to_admins(self, original_fields: dict, method: str, updated_fields: dict = None) -> dict:
        """
        If request.user is in group admin then send email to all users is in group admin.
        Else do not send email.
        """
        user = self.request.user
        group_admin = user.get_admin_group() if not user.is_anonymous else None
        if not group_admin:
            return
        template_context = self._get_template_context(user, original_fields, method, updated_fields)
        to_emails = list(group_admin.user_set.all().values_list("email", flat=True))
        send_email(
            subject=template_context["title"],
            from_email=settings.EMAIL_HOST_USER,
            to_emails=to_emails,
            template_path="email.html",
            template_context=template_context,
        )

    @staticmethod
    def _get_template_context(user, original_fields: dict, method: str, updated_fields: dict = None) -> dict:
        original_fields.pop("_state", None)
        action = ""
        get_item = lambda name, value: {"name": name, "value": value}

        if method == "update":
            action = "UPDATES"

            def get_item(name, value):
                after_value = updated_fields[name]
                if value != after_value:
                    return {"field_name": name, "before": value, "after": after_value}

        elif method == "create":
            action = "CREATES"
        elif method == "destroy":
            action = "DELETES"

        title = f"User '{user.username}' {action} Product id={original_fields['id']}"
        fields = []
        for name, value in original_fields.items():
            item = get_item(name, value)
            if item:
                fields.append(item)
        return {"title": title, "fields": fields, "method": method}
