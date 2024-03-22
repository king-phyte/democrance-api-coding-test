from django.urls import path

from . import views

v1_patterns = (
    [
        path("create_customer/", views.CustomerView.as_view(), name="create-customer"),
        path("quote/", views.QuoteView.as_view(), name="quotes"),
    ],
    "v1",
)
