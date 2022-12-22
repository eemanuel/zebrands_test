from rest_framework import permissions


class CanCRUDProductPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_anonymous:
            return True if view.action in ("retrieve", "list") else False
        group_admin = user.get_admin_group()
        permissions_exists = False
        if group_admin:
            codename = self._get_codename_from_action_to_admins(view.action)
            permissions_exists = group_admin.permissions.filter(codename=codename).exists()
        return permissions_exists or user.is_superuser

    @staticmethod
    def _get_codename_from_action_to_admins(view_action):
        if view_action == "create":
            return "add_product"
        elif view_action in ("retrieve", "list"):
            return "view_product"
        elif view_action in ("update", "partial_update"):
            return "change_product"
        elif view_action == "destroy":
            return "delete_product"
