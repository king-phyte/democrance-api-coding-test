"""
Database models for the API

All models should be placed in this file to serve as a single source of truth, even across
different API versions.
Therefore, if a model is changed in any API version, it will affect all others.
"""

from django.db import models


class Customer(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    date_of_birth = models.DateField(null=False)

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "customers"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def serialize(self):
        """Serializes the customer instance to JSON

        This must be called after the instance has been saved, otherwise the
        fields may be None
        """

        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "dob": self.date_of_birth.strftime("%d-%m-%Y"),
        }
