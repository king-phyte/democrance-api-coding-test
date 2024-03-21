import json

from django.http import JsonResponse
from django.views.generic.edit import ModelFormMixin, ProcessFormView

from api.v1.forms import CustomerCreationForm


class CustomerView(ModelFormMixin, ProcessFormView):
    form_class = CustomerCreationForm

    def post(self, *args, **kwargs):
        """Creates a new customer"""

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
