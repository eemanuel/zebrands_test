from typing import Union

from django.db.models import CharField, FloatField, Model, PositiveIntegerField, QuerySet

__all__ = [
    "Product",
]


class Product(Model):
    sku = CharField(max_length=8, help_text="Stock Keeping Unit")
    name = CharField(max_length=50)
    price = FloatField(max_length=10)
    brand = CharField(max_length=50)
    anonymous_queries_count = PositiveIntegerField(default=0)

    class Meta:
        db_table = "product"

    def __str__(self):
        return f"id={self.id}, name={self.name}, price={self.price}"

    @staticmethod
    def add_to_anonymous_queries_count(obj: Union["Product", QuerySet], value_to_add: int) -> None:
        """
        Add "value_to_add" to each Product.anonymous_queries_count and save it.
        """
        if isinstance(obj, Product):
            obj.anonymous_queries_count += value_to_add
            obj.save(
                update_fields=[
                    "anonymous_queries_count",
                ]
            )
        elif isinstance(obj, QuerySet):
            for product in obj:
                product.anonymous_queries_count += value_to_add
            Product.objects.bulk_update(obj, ["anonymous_queries_count"], batch_size=5_000)
