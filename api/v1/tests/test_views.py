import datetime

from django.test import Client, TestCase
from django.urls import reverse_lazy

from api.models import Customer, Quote


class CustomerTestCase(TestCase):
    # create_customer_url = reverse("api:v1:create_customer")
    create_customer_url = reverse_lazy("api:v1:create-customer")

    def setUp(self):
        self.client = Client()

    def test_create_customer(self):
        user_ben = {"first_name": "Ben", "last_name": "Stokes", "dob": "25-06-1991"}

        response = self.client.post(
            self.create_customer_url,
            user_ben,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json())

        for key in user_ben:
            self.assertIn(key, response.json())
            assert response.json().get(key) == user_ben[key]

    def test_create_customer_with_invalid_data(self):
        # First name is required, but not provided
        response = self.client.post(
            self.create_customer_url,
            {"first_name": "", "last_name": "Stokes", "dob": "25-06-1991"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"]["first_name"][0]["code"], "required")

        # Incorrect date format
        response = self.client.post(
            self.create_customer_url,
            {"first_name": "Ben", "last_name": "Stokes", "dob": "25/06-1991"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"]["dob"][0]["code"], "invalid")


class QuoteTestCase(TestCase):
    def setUp(self):

        self.customer = Customer.objects.create(
            first_name="Ben",
            last_name="Stokes",
            date_of_birth=datetime.date(year=1991, month=6, day=25),
        )
        self.quote = Quote.objects.create(
            customer=self.customer,
            cover=20000,
            premium=200,
            status=Quote.QuoteStatus.NEW,
            type=Quote.QuoteType.PERSONAL_ACCIDENT,
        )

    def test_create_quote(self):
        response = self.client.post(
            "/api/v1/quotes/",
            {
                "customer_id": self.customer.id,
                "type": "personal-accident",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)

        for key in {"id", "customer", "cover", "premium"}:
            self.assertIn(key, response.json())

        self.assertEqual(response.json()["customer"]["id"], self.customer.id)

        # According to the assumption made, people within the ages of 25 and 50 get their
        # cover multiplied by 1.1 and premium by 1.5
        # See :method:`api.v1.forms.QuoteCreationForm.save`
        self.assertEqual(response.json()["cover"], 20000 * 1.1)
        self.assertEqual(response.json()["premium"], 200 * 1.5)

    def test_create_quote_with_invalid_customer_id(self):
        response = self.client.post(
            "/api/v1/quotes/",
            {
                "customer_id": 9999,
                "type": "personal-accident",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual("customer not found", response.json()["detail"])

    def test_accept_quote(self):
        response = self.client.put(
            f"/api/v1/quotes/{self.quote.id}/status/",
            {"status": "accepted"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "accepted")

    def test_pay_for_quote(self):
        response = self.client.put(
            f"/api/v1/quotes/{self.quote.id}/status/",
            {"status": "active"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "active")

    def test_update_nonexistent_quote(self):
        response = self.client.put(
            f"/api/v1/quotes/99999/status/",
            {"status": "accepted"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "quote not found")

    def test_update_quote_with_invalid_status(self):
        response = self.client.put(
            f"/api/v1/quotes/{self.quote.id}/status/",
            {"status": "something"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("invalid quote status", response.json()["detail"])
