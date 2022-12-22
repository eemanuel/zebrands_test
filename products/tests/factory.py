from factory import Faker, LazyAttribute, django
from faker import Faker as faker_faker

from products.models import Product


def _get_sku(obj):
    faker_instance = faker_faker()
    letters = "".join(faker_instance.random_letters(4))
    ints = faker_instance.random_int(1000)
    return f"{letters}{ints}"


class ProductFactory(django.DjangoModelFactory):
    sku = LazyAttribute(_get_sku)
    name = Faker("word")
    price = Faker("pyfloat", positive=True, right_digits=2, max_value=10_000)
    brand = Faker("company")

    class Meta:
        model = Product
