"""Module providing custom field validators for form validation."""

from wtforms import Field, Form


class NotSelecioneValidator:
    """Validator to ensure a field's data is not 'Selecione'.

    Checks that the field data is non-empty and does not equal 'Selecione'.
    """

    def __init__(self, message: str = None) -> None:
        """Initialize the validator.

        Args:
            message: Optional custom error message.

        """
        self.message = message
        self.field_flags = {"required": True}

    def __call__(self, form: Form, field: Field) -> None:
        """Validate the field value.

        Args:
            form: The form instance.
            field: The field to validate.

        Raises:
            StopValidation2Error: If the validation fails.

        Returns:
            None: If the validation passes.

        """
        if not field.data and (isinstance(field.data, str) or not field.data.strip()):
            return

        if field.data != "Selecione":
            return

        message = self.message
        if self.message is None:
            message = field.gettext("This field is required.")

        field.errors[:] = []
        raise StopValidation2Error(message)


class StopValidation2Error(Exception):
    """Exception to signal the end of the validation chain.

    If raised, no further validators will be processed.
    """

    def __init__(self, message: str = "", *args: str | int, **kwargs: str | int) -> None:
        """Initialize the StopValidation2Error exception.

        Args:
            message (str): The error message.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        Exception.__init__(self, message, *args, **kwargs)
