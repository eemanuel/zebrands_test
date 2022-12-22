from rest_framework import routers

from products.views import views

router = routers.SimpleRouter()
router.register("", views.ProductModelViewSet, basename="products")

urlpatterns = router.urls
