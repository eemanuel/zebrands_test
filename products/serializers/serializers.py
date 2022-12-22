from rest_framework.serializers import DecimalField, ModelSerializer, ValidationError

from products.models import Product

__all__ = [
    "ProductSerializer",
]


class ProductSerializer(ModelSerializer):
    price = DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Product
        fields = "__all__"

    def validate_sku(self, sku):
        if not sku.isalnum():
            raise ValidationError("sku must be alphanumeric")
        return sku
