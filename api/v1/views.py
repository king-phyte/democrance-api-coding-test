import json

from django.http import JsonResponse
from django.views.generic.edit import ModelFormMixin, ProcessFormView

from api.models import Customer, Quote
from api.v1.forms import CustomerCreationForm, QuoteCreationForm, QuoteUpdateForm


class CustomerView(ModelFormMixin, ProcessFormView):
    form_class = CustomerCreationForm

    def post(self, *args, **kwargs):
        """Creates a new customer

        HTTP Response Codes
        --------------------
        - 201 Created: Customer created successfully
        - 422 Validation Error: The request body is an invalid JSON or the form validation failed
        """

        try:
            request_json = json.loads(self.request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({"detail": {"request body is malformed"}}, status=422)

        form = self.form_class(request_json)

        if not form.is_valid():
            return JsonResponse(
                {"detail": json.loads(form.errors.as_json())},
                status=422,
            )

        customer = form.save()

        return JsonResponse(customer.serialize(), status=201)


class QuoteView(ProcessFormView):

    def post(self, *args, **kwargs):
        """Create a new quote for a customer

        HTTP Response Codes
        --------------------
        - 201 Created: Quote created successfully
        - 422 Validation Error: The request body is an invalid JSON or the form validation failed
        - 404 Not Found: Customer with specified ID does not exist
        """

        try:
            request_json = json.loads(self.request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({"detail": {"request body is malformed"}}, status=422)

        form = QuoteCreationForm(request_json)

        if not form.is_valid():
            return JsonResponse(
                {"detail": json.loads(form.errors.as_json())},
                status=422,
            )

        try:
            quote = form.save()
        except Customer.DoesNotExist:
            return JsonResponse({"detail": "customer not found"}, status=404)

        return JsonResponse(quote.serialize(), status=201)

    def put(self, *args, **kwargs):
        """Updates a quotes' status (:class:`api.models.Quote.QuoteStatus`)

        This can be used to indicate that a customer has accepted, rejected or paid for the quote.

        Currently, we do not check if the quote belongs to the customer before updating the status.
        Also, consider making a 'state machine' for the status (E.g. new -> accepted -> paid)

        HTTP Response Codes
        --------------------
        - 20O OK: Quote status updated successfully
        - 422 Validation Error: The request body is an invalid JSON or the form validation failed
        - 404 Not Found: Quote with specified ID does not exist
        """

        try:
            request_body_as_dict = json.loads(self.request.body)
        except json.decoder.JSONDecodeError:
            return JsonResponse({"detail": {"request body is malformed"}}, status=422)

        form = QuoteUpdateForm(request_body_as_dict)

        if not form.is_valid():
            return JsonResponse(
                {"detail": json.loads(form.errors.as_json())}, status=422
            )

        try:
            quote = form.save()
        except Quote.DoesNotExist:
            return JsonResponse({"detail": "quote not found"}, status=404)

        return JsonResponse(quote.serialize(), status=200)
