from django.test import Client, TestCase
from django.urls import reverse_lazy


class APITestCase(TestCase):
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
