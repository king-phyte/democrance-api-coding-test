from django import forms

from api.models import Customer


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

    def save(self, *args, **kwargs):
        self.instance = super().save(commit=False)
        self.instance.date_of_birth = self.cleaned_data["dob"]
        self.instance.save()

        return self.instance
