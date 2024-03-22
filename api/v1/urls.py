from django.urls import path

from . import views

v1_patterns = (
    [
        path("create_customer/", views.CustomerView.as_view(), name="create-customer"),
        path("quotes/", views.QuoteCreateView.as_view(), name="create-quotes"),
        path(
            "quotes/<int:quote_id>/status/",
            views.QuoteStatusUpdateView.as_view(),
            name="update-quote-status",
        ),
    ],
    "v1",
)
