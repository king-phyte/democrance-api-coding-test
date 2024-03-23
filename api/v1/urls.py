from django.urls import path

from . import views

v1_patterns = (
    [
        path("create_customer/", views.CustomerView.as_view(), name="create-customer"),
        path("quote/", views.QuoteView.as_view(), name="quotes"),
        path("policies/", views.PolicyListView.as_view(), name="list-policies"),
        path(
            "policies/<int:pk>/",
            views.PolicyDetailView.as_view(),
            name="policy-details",
        ),
        path(
            "policies/<int:pk>/history/",
            views.PolicyHistoryView.as_view(),
            name="policy-history",
        ),
    ],
    "v1",
)
