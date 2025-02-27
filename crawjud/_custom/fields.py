"""Custom fields for Quart-WTF."""

from __future__ import annotations

import itertools
from asyncio import iscoroutinefunction

from quart_wtf import QuartForm
from wtforms import Field, FieldList, Form, ValidationError
from wtforms.fields.core import UnboundField
from wtforms.meta import DefaultMeta
from wtforms.utils import unset_value
from wtforms.validators import StopValidation
from wtforms.widgets import ListWidget

from crawjud._types import AnyType


class QuartBaseForm(Form):
    """Base form class for Quart-WTF."""

    Meta = DefaultMeta
    _meta = None

    @property
    def meta(self) -> AnyType:
        """Get the meta instance."""
        if self._meta is None:
            self._meta = self.Meta()
        return self._meta

    def __init__(self, *args: AnyType, **kwargs: AnyType) -> None:
        """Initialize the form."""
        super().__init__(*args, **kwargs)

    async def validate(self, extra_validators: tuple = None) -> bool:
        """
        Validate the form by calling `validate` on each field.

        :param extra_validators:
            If provided, is a dict mapping field names to a sequence of
            callables which will be passed as extra validators to the field's
            `validate` method.

        Returns `True` if no errors occur.
        """
        success = True
        for name, field in self._fields.items():
            if extra_validators is not None and name in extra_validators:
                extra = extra_validators[name]
            else:
                extra = ()

            if iscoroutinefunction(field.validate):
                if not await field.validate(self, extra):
                    success = False

            else:
                if not field.validate(self, extra):
                    success = False
        return success


class QuartFieldList(FieldList):
    """FieldList subclass to handle dynamic field lists."""

    entries: list[QuartFormField]
    widget = ListWidget()

    def __init__(  # noqa: ANN204, D107
        self,
        unbound_field,  # noqa: ANN001
        label=None,  # noqa: ANN001
        validators=None,  # noqa: ANN001
        min_entries=0,  # noqa: ANN001
        max_entries=None,  # noqa: ANN001
        separator="-",  # noqa: ANN001
        default=(),  # noqa: ANN001
        **kwargs,  # noqa: ANN003
    ):
        # Ensure _prefix is always a string
        kwargs["_prefix"] = kwargs.get("_prefix", "")

        # Initialize name if not provided
        if "name" not in kwargs:
            kwargs["name"] = ""

        super().__init__(label, validators, default=default, **kwargs)
        if self.filters:
            raise TypeError("FieldList does not accept any filters. Instead, define them on the enclosed field.")
        assert isinstance(unbound_field, UnboundField), "Field must be unbound, not a field class"  # noqa: S101 # nosec: B101
        self.unbound_field = unbound_field
        self.min_entries = min_entries
        self.max_entries = max_entries
        self.last_index = -1
        self._separator = separator
        self._field_separator = unbound_field.kwargs.get("separator", "-")

    def process(  # noqa: ANN204, D102, ANN201
        self,
        formdata,  # noqa: ANN001
        data=unset_value,  # noqa: ANN001
        extra_filters=None,  # noqa: ANN001
    ) -> None:
        if extra_filters:
            raise TypeError("FieldList does not accept any filters. Instead, define them on the enclosed field.")

        self.entries = []
        if data is unset_value or not data:
            try:
                data = self.default()
            except TypeError:
                data = self.default

        self.object_data = data

        if formdata:
            indices = sorted(set(self._extract_indices(self.name, formdata)))
            if self.max_entries:
                indices = indices[: self.max_entries]

            idata = iter(data)
            for index in indices:
                try:
                    obj_data = next(idata)
                except StopIteration:
                    obj_data = unset_value
                self._add_entry(formdata, obj_data, index=index)
        else:
            for obj_data in data:
                self._add_entry(formdata, obj_data)

        while len(self.entries) < self.min_entries:
            self._add_entry(formdata)

    async def validate(self, form: Field, extra_validators: tuple = ()) -> bool:
        """
        Validate this FieldList.

        Note that FieldList validation differs from normal field validation in
        that FieldList validates all its enclosed fields first before running any
        of its own validators.
        """
        self.errors = []

        # Run validators on all entries within
        for subfield in self.entries:
            await subfield.validate(form)
            self.errors.append(subfield.errors)

        if not any(x for x in self.errors):
            self.errors = []

        chain = itertools.chain(self.validators, extra_validators)
        self._run_validation_chain(form, chain)

        return len(self.errors) == 0

    def _get_form_field_name(self, index: int) -> str:
        """Get the name for the field at the given index."""
        name = self.name or ""
        if name and self._separator:
            return f"{name}{self._separator}{index}"
        return str(index)

    def _add_entry(self, formdata=None, data=unset_value, index=None):  # noqa: ANN001, ANN202
        """Create a new entry with the given data."""
        assert not self.max_entries or len(self.entries) < self.max_entries, (  # noqa: S101 # nosec: B101
            "You cannot have more than max_entries entries in this FieldList"
        )

        if index is None:
            index = self.last_index + 1
        self.last_index = index

        name = self._get_form_field_name(index)
        field_id = "%s-%s" % (self.id, index) if self.id is not None else None

        field = self.unbound_field.bind(
            form=None, name=name, prefix=self._prefix, id=field_id, _meta=self.meta, translations=self._translations
        )
        field.process(formdata, data)
        self.entries.append(field)
        return field


class QuartFormField(Field):
    """FormField subclass to handle dynamic field lists."""

    def __init__(  # noqa: ANN204, D107
        self,
        form_class,  # noqa: ANN001
        label=None,  # noqa: ANN001
        validators=None,  # noqa: ANN001
        separator="-",  # noqa: ANN001
        **kwargs,  # noqa: ANN003
    ):
        super().__init__(label, validators, **kwargs)
        self.form_class = form_class
        self.separator = separator
        self._obj = None
        if self.filters:
            raise TypeError("FormField cannot take filters, as the encapsulated data is not mutable.")
        if validators:
            raise TypeError("FormField does not accept any validators. Instead, define them on the enclosed form.")

    async def validate(self, form: QuartForm, extra_validators: tuple = ()) -> bool:
        """
        Validate the field and returns True or False. `self.errors` will
        contain any errors raised during validation. This is usually only
        called by `Form.validate`.

        Subfields shouldn't override this, but rather override either
        `pre_validate`, `post_validate` or both, depending on needs.

        :param form: The form the field belongs to.
        :param extra_validators: A sequence of extra validators to run.
        """  # noqa: D205
        self.errors = list(self.process_errors)
        stop_validation = False

        # Check the type of extra_validators
        self.check_validators(extra_validators)

        # Call pre_validate
        try:
            self.pre_validate(form)
        except StopValidation as e:
            if e.args and e.args[0]:
                self.errors.append(e.args[0])
            stop_validation = True
        except ValidationError as e:
            self.errors.append(e.args[0])

        # Run validators
        if not stop_validation:
            chain = itertools.chain(self.validators, extra_validators)
            stop_validation = self._run_validation_chain(form, chain)

        # Call post_validate
        try:
            self.post_validate(form, stop_validation)
        except ValidationError as e:
            self.errors.append(e.args[0])

        return len(self.errors) == 0

    @property
    def data(self) -> dict:
        """Get the data for the field."""
        return self.form.data

    @property
    def errors(self) -> dict:
        """Get the errors for the field."""
        return self.form.errors
