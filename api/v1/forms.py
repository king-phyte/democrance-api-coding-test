"""This module defines forms used by views to perform data cleaning and validation.

In the case of ModelForms, the view will call the form's save method, so it may be necessary to
override that to customize the behavior, but the caller will expect an instance of the model saved
back for serialization.
In the case of exceptions, reraise it so the view (caller) can handle that and convert it to the
appropriate HTTP status code
"""

import datetime

from django import forms

from api.models import Customer, Quote


class CustomerCreationForm(forms.ModelForm):
    """Custom creation form for :class:`api.models.Customer`

    This form also handles saving the model instance, and serializing the model to JSON
    """

    # The input format below is not part of the default (settings.DATE_INPUT_FORMATS)
    # but it is a requirement for this test
    # If this format starts being used a lot, append it to settings.DATE_INPUT_FORMATS
    dob = forms.DateField(input_formats=["%d-%m-%Y"])

    class Meta:
        model = Customer
        # Do not include date_of_birth because the request will contain the field 'dob' instead
        fields = ("first_name", "last_name")

    def save(self, *args, **kwargs) -> Customer:
        self.instance = super().save(commit=False)
        self.instance.date_of_birth = self.cleaned_data["dob"]
        self.instance.save()

        return self.instance


class QuoteCreationForm(forms.ModelForm):
    """Form for creating quotes for the :class:`api.models.Quote` model"""

    customer_id = forms.IntegerField()

    class Meta:
        model = Quote
        fields = ["type"]

    def save(self, *args, **kwargs) -> Quote:
        """Saves a quote and returns it

        :raises Customer.DoesNotExist: If the customer with specified ID does not exist
        """

        try:
            customer = Customer.objects.get(id=self.cleaned_data["customer_id"])
        except Customer.DoesNotExist as err:
            raise err

        # The cover, premium rate and quote band below are based solely on assumption
        if self.cleaned_data["type"] == Quote.QuoteType.PERSONAL_ACCIDENT:
            cover = 20000
            premium = 200
        elif self.cleaned_data["type"] == Quote.QuoteType.AUTO_INSURANCE:
            cover = 30000
            premium = 300
        elif self.cleaned_data["type"] == Quote.QuoteType.HOMEOWNER_INSURANCE:
            cover = 40000
            premium = 400
        else:
            cover = 50000
            premium = 500

        customer_age = (datetime.date.today() - customer.date_of_birth).days // 365

        if customer_age < 25:
            cover *= 1.2
            premium *= 2
        elif 25 <= customer_age < 50:
            cover *= 1.1
            premium *= 1.5
        else:
            cover *= 0.7

        self.instance = Quote.objects.create(
            customer=customer,
            cover=cover,
            premium=premium,
            type=self.cleaned_data["type"],
        )

        return self.instance


class QuoteUpdateForm(forms.ModelForm):
    quote_id = forms.IntegerField()

    class Meta:
        model = Quote
        fields = ["status"]

    def save(self, *args, **kwargs) -> Quote:
        try:
            quote = Quote.objects.get(id=self.cleaned_data["quote_id"])
        except Quote.DoesNotExist as err:
            raise err

        quote.status = self.cleaned_data["status"]
        quote.save()

        return quote
