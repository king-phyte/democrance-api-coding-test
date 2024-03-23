import datetime

from django.test import Client, TestCase
from django.urls import reverse_lazy

from api.models import Customer, Policy, Quote


class CustomerTestCase(TestCase):
    # create_customer_url = reverse("api:v1:create_customer")
    create_customer_url = reverse_lazy("api:v1:create-customer")

    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime.date(year=2000, month=1, day=1),
        )
        self.quote = Quote.objects.create(
            customer=self.customer,
            cover=20000,
            premium=200,
            status=Quote.QuoteStatus.NEW,
            type=Quote.QuoteType.AUTO_INSURANCE,
        )

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

    def test_search_customers(self):
        response = self.client.get("/api/v1/customers/?first_name=John&last_name=Doe")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["customers"]), 1)

        customer = response.json()["customers"][0]

        self.assertEqual(customer["id"], self.customer.id)

        response = self.client.get("/api/v1/customers/?first_name=John")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["customers"]), 1)

        response = self.client.get("/api/v1/customers/?first_name=Ben")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["customers"]), 0)

        response = self.client.get("/api/v1/customers/?dob=01-01-2000")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["customers"]), 1)

        response = self.client.get("/api/v1/customers/?dob=25-06-1991")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["customers"]), 0)

        response = self.client.get("/api/v1/customers/?dob=incorrect")
        self.assertEqual(response.status_code, 422)

        response = self.client.get("/api/v1/customers/?policy_type=auto")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["customers"]), 1)

        response = self.client.get("/api/v1/customers/?policy_type=personal-accident")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["customers"]), 0)

        response = self.client.get("/api/v1/customers/?policy_type=something")
        self.assertEqual(response.status_code, 422)


class QuoteTestCase(TestCase):
    def setUp(self):
        self.client = Client()

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
            "/api/v1/quote/",
            {
                "customer_id": self.customer.id,
                "type": "personal-accident",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)

        for key in {"id", "customer", "cover", "premium", "status", "type"}:
            self.assertIn(key, response.json())

        self.assertEqual(response.json()["customer"]["id"], self.customer.id)

        # According to the assumption made, people within the ages of 25 and 50 get their
        # cover multiplied by 1.1 and premium by 1.5
        # See :method:`api.v1.forms.QuoteCreationForm.save`
        self.assertEqual(response.json()["cover"], 20000 * 1.1)
        self.assertEqual(response.json()["premium"], 200 * 1.5)

        customer_under_25 = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime.date(year=2000, month=1, day=1),
        )

        response = self.client.post(
            "/api/v1/quote/",
            {
                "customer_id": customer_under_25.id,
                "type": "auto",
            },
            content_type="application/json",
        )

        # People below age 25 get their cover multiplied by 1.2 and premium by 2
        self.assertEqual(response.json()["cover"], 30000 * 1.2)
        self.assertEqual(response.json()["premium"], 300 * 2)

        customer_over_50 = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime.date(year=1920, month=12, day=12),
        )

        response = self.client.post(
            "/api/v1/quote/",
            {
                "customer_id": customer_over_50.id,
                "type": "homeowner-insurance",
            },
            content_type="application/json",
        )

        # People above age 50 get their cover multiplied by 0.7 and premium does not change
        self.assertEqual(response.json()["cover"], 40000 * 0.7)
        self.assertEqual(response.json()["premium"], 400)

    def test_create_quote_with_invalid_type(self):
        response = self.client.post(
            "/api/v1/quote/",
            {
                "customer_id": self.customer.id,
                "type": "something-something",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"]["type"][0]["code"], "invalid_choice")

    def test_create_quote_with_invalid_customer_id(self):
        response = self.client.post(
            "/api/v1/quote/",
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
            f"/api/v1/quote/",
            {"quote_id": self.quote.id, "status": "accepted"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "accepted")

    def test_pay_for_quote(self):
        self.client.put(
            f"/api/v1/quote/",
            {"quote_id": self.quote.id, "status": "accepted"},
            content_type="application/json",
        )

        response = self.client.put(
            f"/api/v1/quote/",
            {"quote_id": self.quote.id, "status": "active"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "active")

    def test_update_nonexistent_quote(self):
        response = self.client.put(
            f"/api/v1/quote/",
            {"quote_id": 99999, "status": "accepted"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "quote not found")

    def test_update_quote_with_invalid_status(self):
        response = self.client.put(
            f"/api/v1/quote/",
            {"quote_id": self.quote.id, "status": "something"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json()["detail"]["status"][0]["code"],
            "invalid_choice",
        )


class PolicyTestCase(TestCase):
    def setUp(self):
        self.client = Client()

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

    def test_get_customer_policies(self):
        # We should already have a policy because a quote is created in the setup
        response = self.client.get(
            "/api/v1/policies/",
            data={"customer_id": self.customer.id},
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn("next_cursor", response.json())
        self.assertIn("policies", response.json())

        policies = response.json()["policies"]

        self.assertNotEqual(len(policies), 0)

        for policy in policies:
            for key in {"id", "customer", "cover", "premium", "type", "state"}:
                self.assertIn(key, policy)

            self.assertEqual(policy["customer"]["id"], self.customer.id)

    def test_get_paginated_customer_policies(self):
        self.client.post(
            "/api/v1/quote/",
            {
                "customer_id": self.customer.id,
                "type": "personal-accident",
            },
            content_type="application/json",
        )
        self.client.post(
            "/api/v1/quote/",
            {
                "customer_id": self.customer.id,
                "type": "auto",
            },
            content_type="application/json",
        )

        response = self.client.get(
            "/api/v1/policies/",
            data={"customer_id": self.customer.id, "per_page": 1},
        )

        self.assertEqual(response.status_code, 200)

        self.assertIsNotNone(response.json()["next_cursor"])

        first_policy = response.json()["policies"][0]

        second_policy_response = self.client.get(
            "/api/v1/policies/",
            data={
                "customer_id": self.customer.id,
                "per_page": 1,
                "next_cursor": response.json()["next_cursor"],
            },
        )

        second_policy = second_policy_response.json()["policies"][0]

        self.assertNotEqual(first_policy, second_policy)

    def test_get_customer_policies_with_invalid_query_parameters(self):
        response = self.client.get(
            "/api/v1/policies/",
            data={"customer_id": self.customer.id, "per_page": "a"},
        )

        self.assertEqual(response.status_code, 422)

        self.assertEqual(
            response.json()["detail"],
            "query parameter per_page must be an integer",
        )

    def test_get_policies_without_customer_id(self):
        response = self.client.get("/api/v1/policies/")

        self.assertEqual(response.status_code, 404)

        self.assertEqual(response.json()["detail"], "customer not found")

    def test_get_policy_details(self):
        response = self.client.get(
            "/api/v1/policies/",
            data={"customer_id": self.customer.id, "per_page": 1},
        )

        first_policy = response.json()["policies"][0]
        first_policy_id = first_policy["id"]

        response = self.client.get(f"/api/v1/policies/{first_policy_id}/")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json(), first_policy)

    def test_get_nonexistent_policy_details(self):
        response = self.client.get("/api/v1/policies/9999/")

        self.assertEqual(response.status_code, 404)

        self.assertEqual(response.json()["detail"], "policy not found")

    def test_get_policy_history(self):
        # Accept and pay for quote
        self.client.put(
            f"/api/v1/quote/",
            {"quote_id": self.quote.id, "status": "accepted"},
            content_type="application/json",
        )
        self.client.put(
            f"/api/v1/quote/",
            {"quote_id": self.quote.id, "status": "active"},
            content_type="application/json",
        )

        policy = Policy.objects.get(quote__id=self.quote.id)

        # The policy should have 3 items in its state history (quoted -> new -> bound)

        response = self.client.get(
            f"/api/v1/policies/{policy.id}/history/",
            # Limit to 2 per page so we can test pagination
            data={"per_page": 2},
        )

        self.assertEqual(response.status_code, 200)

        self.assertIn("next_cursor", response.json())
        self.assertIsNotNone(response.json()["next_cursor"])

        next_cursor = response.json()["next_cursor"]

        self.assertIn("history", response.json())

        history = response.json()["history"]

        for item in history:
            for key in {"id", "state", "object_json_dump", "policy"}:
                self.assertIn(key, item)

        newer = history[0]
        older = history[1]

        # Items in the history have the same policy id
        self.assertEqual(newer["policy"]["id"], older["policy"]["id"])

        # but different status
        self.assertNotEqual(newer["state"], older["state"])

        # and they are in descending order by creation time
        self.assertGreater(newer["created"], older["created"])

        response = self.client.get(
            f"/api/v1/policies/{policy.id}/history/",
            data={"per_page": 2, "next_cursor": next_cursor},
        )

        third = response.json()["history"][0]

        # No two items in the history should be the same
        self.assertNotEqual(newer, third)
        self.assertNotEqual(older, third)

    def test_get_nonexistent_policy_history(self):
        response = self.client.get("/api/v1/policies/9999/history/")

        self.assertEqual(response.status_code, 404)

        self.assertEqual(response.json()["detail"], "policy not found")
