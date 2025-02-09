"""Module providing custom field validators for form validation."""


class NotSelecioneValidator:
    """Validator to ensure a field's data is not 'Selecione'.

    Checks that the field data is non-empty and does not equal 'Selecione'.
    """

    def __init__(self, message=None):
        """Initialize the validator.

        Args:
            message: Optional custom error message.

        """
        self.message = message
        self.field_flags = {"required": True}

    def __call__(self, form, field):
        """Validate the field value.

        Args:
            form: The form instance.
            field: The field to validate.

        Raises:
            StopValidation2: If the validation fails.

        """
        if not field.data and (isinstance(field.data, str) or not field.data.strip()):
            return

        if field.data != "Selecione":
            return

        message = self.message
        if self.message is None:
            message = field.gettext("This field is required.")

        field.errors[:] = []
        raise StopValidation2(message)


class StopValidation2(Exception):
    """Exception to signal the end of the validation chain.

    If raised, no further validators will be processed.
    """

    def __init__(self, message="", *args, **kwargs):
        """Initialize the StopValidation2 exception.

        Args:
            message (str): The error message.

        """
        Exception.__init__(self, message, *args, **kwargs)
