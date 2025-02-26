"""Module that aggregates configuration forms for the application."""

from .admin import UserForm, UserFormEdit
from .super_admin import BotLicenseAssociationForm, ClienteForm

__all__ = [UserForm, UserFormEdit, ClienteForm, BotLicenseAssociationForm]
