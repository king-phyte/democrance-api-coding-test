import datetime

from django.test import TestCase

from api.models import Customer


class TestModels(TestCase):
    def test_create_customer(self):
        customer = Customer.objects.create(
            first_name="Ben",
            last_name="Stokes",
            date_of_birth=datetime.date(year=1991, month=6, day=25),
        )

        self.assertEqual(customer.id, 1)
        self.assertIsNotNone(customer.created)
        self.assertIsNotNone(customer.last_modified)
