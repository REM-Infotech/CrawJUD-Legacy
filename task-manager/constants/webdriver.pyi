from typing import Literal, TypedDict

ARGUMENTS: list[str]

class _DESTINATIONS(TypedDict):
    id: Literal["Save as PDF"]
    origin: Literal["local"]
    account: Literal[""]

class _SETTINGS(TypedDict):
    recentDestinations: list[_DESTINATIONS]
    selectedDestinationId: Literal["Save as PDF"]
    version: Literal[2]

DESTINATIONS = TypedDict(
    "recentDestinations",
    {
        "id": Literal["Save as PDF"],
        "origin": Literal["local"],
        "account": Literal[""],
    },
)()

SETTINGS = TypedDict(
    "PrintingPreviewSettings",
    {
        "recentDestinations": list[_DESTINATIONS],
        "selectedDestinationId": Literal["Save as PDF"],
        "version": Literal[2],
    },
)()

PREFERENCES = TypedDict(
    "ChromePreferences",
    {
        "download.prompt_for_download": bool,
        "plugins.always_open_pdf_externally": bool,
        "profile.default_content_settings.popups": int,
        "printing.print_preview_sticky_settings.appState": _SETTINGS,
        "download.default_directory": str,
        "credentials_enable_service": bool,
        "profile.password_manager_enabled": bool,
    },
)()
