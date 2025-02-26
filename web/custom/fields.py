"""Custom fields for Quart-WTF."""

from __future__ import annotations

import itertools

from quart_wtf import QuartForm
from wtforms import Field, FieldList, FormField, ValidationError
from wtforms.validators import StopValidation


class QuartFieldList(FieldList):
    """FieldList subclass to handle dynamic field lists."""

    entries: list[QuartFormField]

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


class QuartFormField(FormField):
    """FormField subclass to handle dynamic field lists."""

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
