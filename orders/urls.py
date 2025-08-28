from django.urls import path

from .my_views import process_order


urlpatterns = [
    path('<int:order_id>/processOrder', process_order, name='process_order'),
]
