import json

from django.http import Http404, JsonResponse
from django.views.generic.detail import BaseDetailView, SingleObjectMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView

from api.models import Customer, Policy, PolicyStateHistory, Quote
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

        Body parameters
        ---------------
            - customer_id (Required): The id of the customer
            - type (Required): The new type of quote

            See: :class:`api.v1.forms.QuoteCreationForm`


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

        The state is changed only if it follows the transition (new -> accepted -> active).
        Currently, we do not check if the quote belongs to the customer before updating the status.

        Body parameters
        ---------------
            - quote_id (Required): The id of the quote to update
            - status (Required): The new status of the quote

            See: :class:`api.v1.forms.QuoteUpdateForm`

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


class PolicyListView(ProcessFormView):
    def get(self, *args, **kwargs):
        """Get a list of a customer's policies

        The results are returned in ascending order of policy creation and are paginated by cursor.

        Query parameters
        ----------------
            - per_page (Optional): The number of items to return per page. Default is 10. Max is 100

            - next_cursor (Optional): The next cursor to use for fetching the next set of policies.
              This should not be guessed.

        HTTP Response Codes
        --------------------
            - 20O OK: Success
            - 422 Validation Error: The query parameters are invalid
            - 404 Not Found: Customer with specified ID does not exist
        """

        customer_id = self.request.GET.get("customer_id", 0)

        if not customer_id:
            return JsonResponse({"detail": "customer not found"}, status=404)

        try:
            per_page = int(self.request.GET.get("per_page", 10))
        except ValueError:
            return JsonResponse(
                {"detail": "query parameter per_page must be an integer"},
                status=422,
            )

        # Force the maximum per page to be 100
        per_page = min(per_page, 100)

        # If leaking internal IDs is undesired, we can make the cursor opaque using base64 or similar
        try:
            next_cursor = int(self.request.GET.get("next_cursor", 1))
        except ValueError:
            # We assume we are not the one who provided the cursor (because we sent integers)
            # Therefore, we start from the first set
            next_cursor = None

        policies = Policy.objects.filter(customer__id=customer_id).order_by("id")

        if next_cursor is not None:
            policies = policies.filter(id__gte=next_cursor)

        # Fetch one more than per_page, so that the extra item becomes the cursor
        policies = list(policies[: per_page + 1])

        last_policy_id = None

        if len(policies) > per_page:
            last_policy_id = policies.pop().id

        return JsonResponse(
            {
                "next_cursor": last_policy_id,
                "policies": [policy.serialize() for policy in policies],
            },
            status=200,
        )


class PolicyDetailView(BaseDetailView):
    model = Policy

    def get(self, *args, **kwargs):
        """Get details about a policy

        HTTP Response Codes
        --------------------
            - 20O OK: Success
            - 404 Not Found: Policy with specified ID does not exist
        """

        try:
            policy = self.get_object()
        except Http404:
            return JsonResponse({"detail": "policy not found"}, status=404)

        return JsonResponse(policy.serialize(), status=200)


class PolicyHistoryView(SingleObjectMixin, ProcessFormView):
    model = Policy

    def get(self, *args, **kwargs):
        """Get the state history of a policy

        If the policy exists, then it will have at least one state history entry.
        The results are returned in descending order of state change time.

        Query parameters
        ----------------
            - per_page (Optional): The number of items to return per page. Default is 10. Max is 100

            - next_cursor (Optional): The next cursor to use for fetching the next set of state history entries.
              This should not be guessed.

        HTTP Response Codes
        --------------------
            - 20O OK: Success
            - 422 Validation Error: The query parameters are invalid
            - 404 Not Found: Customer with specified ID does not exist
        """

        try:
            policy = self.get_object()
        except Http404:
            return JsonResponse({"detail": "policy not found"}, status=404)

        try:
            per_page = int(self.request.GET.get("per_page", 10))
        except ValueError:
            return JsonResponse(
                {"detail": "query parameter per_page must be an integer"},
                status=422,
            )

        # Force the maximum per page to be 100
        per_page = min(per_page, 100)

        # If leaking internal IDs is undesired, we can make the cursor opaque using base64 or similar
        next_cursor = self.request.GET.get("next_cursor", None)

        if next_cursor is not None:
            try:
                next_cursor = int(next_cursor)
            except ValueError:
                # We assume we are not the one who provided the cursor (because we sent integers)
                # Therefore, we start from the first set
                next_cursor = None

        history = PolicyStateHistory.objects.filter(policy__id=policy.id).order_by(
            "-id"
        )

        if next_cursor is not None:
            history = history.filter(id__lte=next_cursor)

        # Fetch one more than per_page, so that the extra item becomes the cursor
        history = list(history[: per_page + 1])

        last_history_id = None

        if len(history) > per_page:
            last_history_id = history.pop().id

        return JsonResponse(
            {
                "next_cursor": last_history_id,
                "history": [h.serialize() for h in history],
            },
            status=200,
        )
