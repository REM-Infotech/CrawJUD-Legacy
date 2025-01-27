import FindMyIP as ip
import httpx
from dotenv import dotenv_values

TOKEN = dotenv_values().get("TOKEN_IP2")


class GlobalExcept(Exception):
    """Exceção base personalizada."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NetworkError(GlobalExcept):
    """Exceção para quando um recurso não é encontrado."""

    def __init__(self, message: str = "You are not connected to the internet!!"):
        super().__init__(message)


class InfoGeoloc:

    data: dict[str, str, int | bool] = {}

    def __init__(self):
        ip_external = ip.external()
        if not ip_external:
            raise NetworkError()

        get_geoloc = self.IP2Location(ip_external)
        for key, value in get_geoloc.items():
            self.data.update({f"_{key}": value})

    def __getattr__(self, name: str) -> str:

        item = self.data.get(name, None)
        if not item:
            raise AttributeError(
                f"Atributo '{name}' não encontrado na classe '{self.__class__.__name__}'"
            )

        return item

    def IP2Location(self, ip: str) -> dict[str, str] | None:
        data = httpx.get(
            "https://api.ip2location.io/?key={key}&ip={ip}".format(key=TOKEN, ip=ip)
        )
        return data.json()

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def country_code(self) -> str:
        return self._country_code

    @property
    def country_name(self) -> str:
        return self._country_name

    @property
    def region_name(self) -> str:
        return self._region_name

    @property
    def city_name(self) -> str:
        return self._city_name

    @property
    def latitude(self) -> str:
        return self._latitude

    @property
    def longitude(self) -> str:
        return self._longitude

    @property
    def zip_code(self) -> str:
        return self._zip_code

    @property
    def time_zone(self) -> str:
        return self._time_zone

    @property
    def asn(self) -> str:
        return self._asn

    @property
    def as_name(self) -> str:
        return self._as_name

    @property
    def is_proxy(self) -> bool:
        return self._is_proxy


class GeoLoc(InfoGeoloc):
    def __init__(self, *args, **kwrgs):
        super().__init__(*args, **kwrgs)
