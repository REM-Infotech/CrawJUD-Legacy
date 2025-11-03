"""Constantes para webdriver."""

SETTINGS = {
    "recentDestinations": [
        {"id": "Save as PDF", "origin": "local", "account": ""},
    ],
    "selectedDestinationId": "Save as PDF",
    "version": 2,
}


ARGUMENTS = [
    "--ignore-ssl-errors=yes",
    "--ignore-certificate-errors",
    "--display=:0",
    "--window-size=1280,720",
    "--no-sandbox",
    "--kiosk-printing",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-software-rasterizer",
    "--disable-renderer-backgrounding",
    "--disable-backgrounding-occluded-windows",
    "--disable-blink-features=AutomationControlled",
    "--disable-features=MediaFoundationVideoCapture",
    "--disable-software-rasterizer",
    "--disable-features=VizDisplayCompositor",
]


PREFERENCES = {
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True,
    "profile.default_content_settings.popups": 0,
    "printing.print_preview_sticky_settings.appState": {},
    "download.default_directory": "",
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
}
