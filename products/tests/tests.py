from django.conf import settings
from django.core import mail
from django.urls import reverse

from pytest import fixture, mark
from rest_framework import status
from rest_framework.test import APIClient

from authentication.tests.factory import UserFactory
from products.models import Product
from products.tests.factory import ProductFactory


class TestProductModelViewSet:
    @fixture(autouse=True)
    def set_up(self):
        self.user = None
        self.request_data = {
            "sku": "A1b2C3d4",
            "name": "Candy",
            "price": 777.55,
            "brand": "ArCor",
        }
        self.client = APIClient()

    # private methods
    def _login_user(self, with_admin_group=True):
        self.user = UserFactory(with_admin_group=with_admin_group)
        self.client.login(username=self.user.username, password="admin")

    def _post_data(self, data):
        return self.client.post(reverse("products-list"), data, format="json")

    def _retrieve_data(self, pk):
        return self.client.get(reverse("products-detail", kwargs={"pk": pk}), format="json")

    def _list_data(self):
        return self.client.get(reverse("products-list"), format="json")

    def _put_data(self, data, pk):
        return self.client.put(reverse("products-detail", kwargs={"pk": pk}), data, format="json")

    def _patch_data(self, data, pk):
        return self.client.patch(reverse("products-detail", kwargs={"pk": pk}), data, format="json")

    def _destroy_data(self, pk):
        return self.client.delete(reverse("products-detail", kwargs={"pk": pk}), format="json")

    # tests
    def _check_outbox(self, to_emails_len, user_not_admin=None):
        assert len(mail.outbox) == 1
        sended_email = mail.outbox[0]
        assert self.user.username in mail.outbox[0].subject
        assert sended_email.from_email == settings.EMAIL_HOST_USER
        assert len(sended_email.to) == to_emails_len
        if user_not_admin:
            assert user_not_admin.email not in sended_email.to
        assert sended_email.body == ""
        assert len(sended_email.alternatives) == 1
        assert sended_email.alternatives[0] != ""

    @mark.success
    @mark.django_db
    def test_admin_create_success(self):
        """Login User with "Administrator" Group. Then check "create" works successfully"""
        assert Product.objects.count() == 0

        self._login_user(with_admin_group=True)
        response = self._post_data(data=self.request_data)

        assert Product.objects.count() == 1
        self._check_outbox(to_emails_len=1)
        assert response.status_code == status.HTTP_201_CREATED

    @mark.parametrize("login_user", [True, False])
    @mark.success
    @mark.django_db
    def test_list_success(self, login_user):
        """Login User with "Administrator" Group. Then check "list" works successfully"""
        ids = []
        for _ in range(3):
            product = ProductFactory(anonymous_queries_count=0)
            ids.append(product.id)

        expected_anonymous_queries = 1
        if login_user:
            expected_anonymous_queries = 0
            self._login_user(with_admin_group=True)
        response = self._list_data()

        for item in response.data:
            assert item["brand"] is not None
            assert item["id"] in ids
            assert item["name"] is not None
            assert item["price"] is not None
            assert item["sku"] is not None
            assert item["anonymous_queries_count"] == expected_anonymous_queries
        for product in Product.objects.filter(id__in=ids):
            assert product.anonymous_queries_count == expected_anonymous_queries

        assert len(mail.outbox) == 0
        assert response.status_code == status.HTTP_200_OK

    @mark.parametrize("login_user", [True, False])
    @mark.success
    @mark.django_db
    def test_retrieve_success(self, login_user):
        """Login User with "Administrator" Group. Then check "retrieve" works successfully"""
        product = ProductFactory()

        expected_anonymous_queries = 1
        if login_user:
            expected_anonymous_queries = 0
            self._login_user(with_admin_group=True)
        response = self._retrieve_data(pk=product.id)

        data = response.data
        product.refresh_from_db()
        assert data["brand"] == product.brand
        assert data["id"] == product.id
        assert data["name"] == product.name
        assert float(data["price"]) == product.price
        assert data["sku"] == product.sku
        assert data["anonymous_queries_count"] == product.anonymous_queries_count == expected_anonymous_queries

        assert len(mail.outbox) == 0
        assert response.status_code == status.HTTP_200_OK

    @mark.success
    @mark.django_db
    def test_admin_put_success(self):
        """Login User with "Administrator" Group. Then check "put" works successfully"""
        UserFactory(with_admin_group=True)
        UserFactory(with_admin_group=True)
        user_not_admin = UserFactory(with_admin_group=False)
        product = ProductFactory(**self.request_data)
        request_data = {
            "sku": "00zz00zz",
            "name": "Beer",
            "price": 100,
            "brand": "Guiness",
        }

        self._login_user(with_admin_group=True)
        response = self._put_data(data=request_data, pk=product.id)

        data = response.data
        # Isn't called product.refresh_from_db()
        assert data["anonymous_queries_count"] == product.anonymous_queries_count == 0
        assert data["brand"] == request_data["brand"] != product.brand
        assert data["id"] == product.id
        assert data["name"] == request_data["name"] != product.name
        assert float(data["price"]) == request_data["price"] != int(product.price)
        assert data["sku"] == request_data["sku"] != product.sku

        self._check_outbox(3, user_not_admin)
        assert response.status_code == status.HTTP_200_OK

    @mark.success
    @mark.django_db
    def test_admin_patch_success(self):
        """Login User with "Administrator" Group. Then check "patch" works successfully"""
        UserFactory(with_admin_group=True)
        UserFactory(with_admin_group=True)
        user_not_admin = UserFactory(with_admin_group=False)
        product = ProductFactory(**self.request_data)
        request_data = {"price": 100}

        self._login_user(with_admin_group=True)
        response = self._patch_data(data=request_data, pk=product.id)

        data = response.data
        # Isn't called product.refresh_from_db()
        assert data["anonymous_queries_count"] == product.anonymous_queries_count == 0
        assert data["brand"] == product.brand
        assert data["id"] == product.id
        assert data["name"] == product.name
        assert float(data["price"]) == request_data["price"] != int(product.price)
        assert data["sku"] == product.sku

        self._check_outbox(3, user_not_admin)
        assert response.status_code == status.HTTP_200_OK

    @mark.success
    @mark.django_db
    def test_admin_destroy_success(self):
        """Login User with "Administrator" Group. Then check "destroy" works successfully"""
        product = ProductFactory()
        assert Product.objects.count() == 1

        self._login_user(with_admin_group=True)
        response = self._destroy_data(pk=product.id)

        assert Product.objects.count() == 0
        self._check_outbox(to_emails_len=1)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @mark.error
    @mark.django_db
    def test_create_bad_data_error(self):
        """
        Login User with "Administrator" Group.
        Then check "create" returns 400 using wrogn data.
        """
        request_data = {
            "sku": "a" * 9,
            "name": True,
            "price": 777.555,
            "brand": [1, 2, 3],
        }
        assert Product.objects.count() == 0
        self._login_user(with_admin_group=True)
        response = self._post_data(data=request_data)

        data = response.data
        assert str(data["brand"][0]) == "Not a valid string."
        assert str(data["name"][0]) == "Not a valid string."
        assert str(data["price"][0]) == "Ensure that there are no more than 2 decimal places."
        assert str(data["sku"][0]) == "Ensure this field has no more than 8 characters."

        assert Product.objects.count() == 0
        assert len(mail.outbox) == 0
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @mark.forbidden
    @mark.django_db
    def test_create_forbidden(self):
        """Login User without "Administrator" Group. Then check "create" returns 403"""
        self._login_user(with_admin_group=False)
        response = self._post_data(data=self.request_data)
        assert Product.objects.count() == 0
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @mark.forbidden
    @mark.django_db
    def test_list_forbidden(self):
        """Login User without "Administrator" Group. Then check "list" returns 403"""
        self._login_user(with_admin_group=False)
        response = self._list_data()
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @mark.forbidden
    @mark.django_db
    def test_retrieve_forbidden(self):
        """Login User without "Administrator" Group. Then check "retrieve" returns 403"""
        product = ProductFactory()
        self._login_user(with_admin_group=False)
        response = self._retrieve_data(pk=product.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @mark.forbidden
    @mark.django_db
    def test_put_forbidden(self):
        """Login User without "Administrator" Group. Then check "put" returns 403"""
        product = ProductFactory(**self.request_data)
        self._login_user(with_admin_group=False)
        response = self._put_data(data=self.request_data, pk=product.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @mark.forbidden
    @mark.django_db
    def test_patch_forbidden(self):
        """Login User without "Administrator" Group. Then check "patch" returns 403"""
        product = ProductFactory(**self.request_data)
        request_data = {"price": 100}
        self._login_user(with_admin_group=False)
        response = self._patch_data(data=request_data, pk=product.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @mark.forbidden
    @mark.django_db
    def test_destroy_forbidden(self):
        """Login User without "Administrator" Group. Then check "destroy" returns 403"""
        product = ProductFactory()
        self._login_user(with_admin_group=False)
        assert Product.objects.count() == 1
        response = self._destroy_data(pk=product.id)
        assert Product.objects.count() == 1
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @mark.unauthorized
    @mark.django_db
    def test_create_anonymous_user_unauthorized(self):
        """Not Login User" Group. Then check "delete" returns 401"""
        response = self._post_data(data=self.request_data)  # without login
        assert Product.objects.count() == 0
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @mark.unauthorized
    @mark.django_db
    def test_put_anonymous_user_unauthorized(self):
        """Not Login User" Group. Then check "delete" returns 401"""
        product = ProductFactory(**self.request_data)
        response = self._put_data(data=self.request_data, pk=product.id)  # without login
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @mark.unauthorized
    @mark.django_db
    def test_patch_anonymous_user_unauthorized(self):
        """Not Login User" Group. Then check "delete" returns 401"""
        product = ProductFactory(**self.request_data)
        request_data = {"price": 100}
        response = self._patch_data(data=request_data, pk=product.id)  # without login
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @mark.unauthorized
    @mark.django_db
    def test_destroy_anonymous_user_unauthorized(self):
        """Not Login User" Group. Then check "destroy" returns 401"""
        product = ProductFactory()
        assert Product.objects.count() == 1
        response = self._destroy_data(pk=product.id)  # without login
        assert Product.objects.count() == 1
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
