from django.urls import path
from apps.payments.views import PaymentCreateView, PaymentDetailView, PaymentListView

urlpatterns = [
    path("",         PaymentListView.as_view(),   name="payment-list"),
    path("create/",  PaymentCreateView.as_view(),  name="payment-create"),
    path("<uuid:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
]
