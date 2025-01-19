from gevent import monkey

monkey.patch_all(aggressive=False)


import FindMyIP as ip
import httpx
from dotenv import dotenv_values

TOKEN = dotenv_values().get("TOKEN_IP2")


class GlobalExcept(Exception):  # pragma: no cover
    """Exceção base personalizada."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NetworkError(GlobalExcept):  # pragma: no cover
    """Exceção para quando um recurso não é encontrado."""

    def __init__(self, message: str = "You are not connected to the internet!!"):
        super().__init__(message)


class InfoGeoloc:

    data: dict[str, str, int | bool] = {}

    def __init__(self):
        ip_external = ip.external()
        if not ip_external:  # pragma: no cover
            raise NetworkError()

        get_geoloc = self.IP2Location(ip_external)
        for key, value in get_geoloc.items():
            self.data.update({f"_{key}": value})

    def __getattr__(self, name: str) -> str:

        item = self.data.get(name, None)
        if not item:  # pragma: no cover
            raise AttributeError(
                f"Atributo '{name}' não encontrado na classe '{self.__class__.__name__}'"
            )

        return item

    def IP2Location(self, ip: str) -> dict[str, str] | None:

        with httpx.Client() as client:
            data = client.get(
                "https://api.ip2location.io/?key={key}&ip={ip}".format(key=TOKEN, ip=ip)
            )

        return data.json()

    @property
    def ip(self) -> str:
        return self._ip  # pragma: no cover

    @property
    def country_code(self) -> str:
        return self._country_code  # pragma: no cover

    @property
    def country_name(self) -> str:
        return self._country_name  # pragma: no cover

    @property
    def region_name(self) -> str:
        return self._region_name  # pragma: no cover

    @property
    def city_name(self) -> str:
        return self._city_name  # pragma: no cover

    @property
    def latitude(self) -> str:
        return self._latitude  # pragma: no cover

    @property
    def longitude(self) -> str:
        return self._longitude  # pragma: no cover

    @property
    def zip_code(self) -> str:
        return self._zip_code  # pragma: no cover

    @property
    def time_zone(self) -> str:
        return self._time_zone  # pragma: no cover

    @property
    def asn(self) -> str:
        return self._asn  # pragma: no cover

    @property
    def as_name(self) -> str:
        return self._as_name  # pragma: no cover

    @property
    def is_proxy(self) -> bool:
        return self._is_proxy  # pragma: no cover


class GeoLoc(InfoGeoloc):
    def __init__(self, *args, **kwrgs):
        super().__init__(*args, **kwrgs)
