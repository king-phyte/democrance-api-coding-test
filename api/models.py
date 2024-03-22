"""
Database models for the API

All models should be placed in this file to serve as a single source of truth, even across
different API versions.
Therefore, if a model is changed in any API version, it will affect all others.
"""

from django.core.serializers.json import DjangoJSONEncoder
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
        """Serializes the customer instance to dict

        This must be called after the instance has been saved, otherwise the
        fields may be None
        """

        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "dob": self.date_of_birth.strftime("%d-%m-%Y"),
        }


class Quote(models.Model):
    class QuoteStatus(models.TextChoices):
        NEW = "new"
        ACCEPTED = "accepted"
        REJECTED = "rejected"
        ACTIVE = "active"

    class QuoteType(models.TextChoices):
        PERSONAL_ACCIDENT = "personal-accident"
        HOMEOWNER_INSURANCE = "homeowner-insurance"
        AUTO_INSURANCE = "auto"

    id = models.BigAutoField(primary_key=True)
    status = models.CharField(
        max_length=20,
        choices=QuoteStatus,
        default=QuoteStatus.NEW,
    )
    type = models.CharField(max_length=20, null=False, blank=False, choices=QuoteType)
    premium = models.DecimalField(max_digits=8, decimal_places=2)
    cover = models.DecimalField(max_digits=10, decimal_places=2)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "quotes"

    def save(self, *args, **kwargs):
        """Save the current instance

        If the current instance is new, a policy will be created for it.
        Hence, for new quotes, this method behaves like an AFTER INSERT trigger
        """

        is_new_quote = False

        if not self.pk:
            is_new_quote = True

        super().save(*args, **kwargs)

        if is_new_quote:
            Policy.objects.create(
                customer=self.customer,
                quote=self,
                state=Policy.PolicyState.QUOTED,
                type=self.type,
                cover=self.cover,
                premium=self.premium,
            )

    def serialize(self):
        """Serializes the quote instance to dict

        This must be called after the instance has been saved, otherwise the
        fields may be None
        """

        return {
            "id": self.id,
            "status": self.status,
            "type": self.type,
            "premium": self.premium,
            "cover": self.cover,
            "customer": self.customer.serialize(),
        }


class PolicyStateHistory(models.Model):
    """This class represents an append-only (log) table that is used to track the state changes of policies

    A better solution *may* have been to use temporal tables, but SQLite (and PostgreSQL)
    does not have that, so we override save and similar methods to
    implement it manually (simulating triggers).
    See: :method:`Policy.save`
    """

    id = models.BigAutoField(primary_key=True)

    # If we delete a policy, then delete its state history
    policy = models.ForeignKey("Policy", on_delete=models.CASCADE)
    state = models.CharField(max_length=20)

    # The default encoder cannot handle Decimal fields
    as_json = models.JSONField(encoder=DjangoJSONEncoder)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "policy_state_history"

    def serialize(self):
        """Serialize the policy history as a dict"""

        return {
            "id": self.id,
            "state": self.state,
            "object_json_dump": self.as_json,
            "policy": self.policy.serialize(),
            "created": self.created,
        }


class Policy(models.Model):
    class PolicyState(models.TextChoices):
        QUOTED = "quoted"
        NEW = "new"
        BOUND = "bound"

    id = models.BigAutoField(primary_key=True)

    type = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        # The quote types are translated to policy types, I suppose
        choices=Quote.QuoteType,
    )
    state = models.CharField(
        max_length=20,
        choices=PolicyState,
        default=PolicyState.QUOTED,
    )
    premium = models.DecimalField(max_digits=8, decimal_places=2)
    cover = models.DecimalField(max_digits=10, decimal_places=2)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, on_delete=models.RESTRICT)

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "policies"

    def save(self, *args, **kwargs):
        """Save the current instance

        This method inserts a new PolicyStateHistory every time it is called (by design).
        As such, only call it when the state of the policy changed, such as is
        done by :class:`api.v1.forms.QuoteUpdateForm`
        """

        super().save(*args, **kwargs)

        PolicyStateHistory.objects.create(
            policy=self,
            state=self.state,
            as_json=self.serialize(),
        )

    def serialize(self):
        return {
            "id": self.id,
            "type": self.type,
            "state": self.state,
            "premium": self.premium,
            "cover": self.cover,
            "customer": self.customer.serialize(),
            "quote": self.quote.serialize(),
        }
