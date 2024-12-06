import re

from dotenv import dotenv_values


def csp() -> dict[str]:  # pragma: no cover

    from app.models import Servers

    srvs = Servers.query.all()
    csp_vars = {
        "default-src": ["'self'"],
        "script-src": [
            "'self'",
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com",
            "https://cdn.datatables.net",
            "https://unpkg.com",
            "https://code.jquery.com",
            "https://use.fontawesome.com",
            "",
            "'unsafe-inline'",
        ],
        "style-src": [
            "'self'",
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com",
            "https://cdn.datatables.net",
            "https://unpkg.com",
            "https://github.com",
            "https://avatars.githubusercontent.com",
            "'unsafe-inline'",
        ],
        "img-src": [
            "'self'",
            "data:",
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com",
            "https://cdn.datatables.net",
            "https://unpkg.com",
            "https://cdn-icons-png.flaticon.com",
            "https://github.com",
            "https://domain.cliente.com",
            "https://avatars.githubusercontent.com",
        ],
        "connect-src": [
            "'self'",
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com",
            "https://cdn.datatables.net",
            "https://github.com",
            "https://unpkg.com",
            "https://avatars.githubusercontent.com",
        ],
        "frame-src": [
            "'self'",
            "https://domain.cliente.com",
            "https://github.com",
            "https://avatars.githubusercontent.com",
        ],
    }
    if srvs:
        for srv in srvs:
            csp_vars.get("connect-src").append(f"https://{srv.address}")
            csp_vars.get("connect-src").append(f"wss://{srv.address}")

    return csp_vars


def check_allowed_origin(origin="https://google.com"):  # pragma: no cover
    allowed_origins = [
        r"https:\/\/.*\.nicholas\.dev\.br",
        r"https:\/\/.*\.robotz\.dev",
        r"https:\/\/.*\.rhsolutions\.info",
        r"https:\/\/.*\.rhsolut\.com\.br",
    ]
    if not origin:
        origin = f'https://{dotenv_values().get("HOSTNAME")}'

    for orig in allowed_origins:
        pattern = orig
        matchs = re.match(pattern, origin)
        if matchs:
            return True

    return False
