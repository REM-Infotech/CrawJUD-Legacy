"""Module for retrieving and handling geolocation information based on IP."""

import json
from os import environ

import FindMyIP as ip  # noqa: N813
from dotenv_vault import load_dotenv
from tornado.httpclient import HTTPClient

TOKEN = environ.get("TOKEN_IP2")
load_dotenv()


class GlobalExcept(Exception):  # noqa: N818
    """Base custom exception class for global errors."""

    def __init__(self, message: str) -> None:
        """Initialize GlobalExcept with an error message.

        Args:
            message (str): The error message.

        """
        super().__init__(message)
        self.message = message


class NetworkError(GlobalExcept):
    """Exception raised when a network-related error occurs."""

    def __init__(self, message: str = "You are not connected to the internet!!") -> None:
        """Initialize NetworkError with a default or custom message.

        Args:
            message (str, optional): The error message. Defaults to a predefined message.

        """
        super().__init__(message)


class InfoGeoloc:
    """Class to retrieve and store geolocation information based on external IP."""

    data: dict[str, str, int | bool] = {}

    def __init__(self) -> None:
        """Initialize InfoGeoloc by fetching geolocation data."""
        ip_external = ip.external()
        if not ip_external:
            raise NetworkError

        get_geoloc = self.IP2Location(ip_external)
        for key, value in get_geoloc.items():
            self.data.update({f"_{key}": value})

    def __getattr__(self, name: str) -> str:
        """Retrieve attribute from geolocation data.

        Args:
            name (str): The name of the attribute to retrieve.

        Raises:
            AttributeError: If the attribute does not exist.

        Returns:
            str: The value of the requested attribute.

        """
        item = self.data.get(name, None)
        if not item:
            raise AttributeError(f"Atributo '{name}' não encontrado na classe '{self.__class__.__name__}'")

        return item

    def IP2Location(self, ip: str) -> dict[str, str] | None:  # noqa: N802
        """Fetch geolocation data for a given IP address using IP2Location API.

        Args:
            ip (str): The IP address to lookup.

        Returns:
            dict[str, str] | None: Geolocation data if successful, else None.

        """
        client = HTTPClient()
        url = f"https://api.ip2location.io/?key={TOKEN}&ip={ip}"
        data = client.fetch(url)
        return json.loads(data.body.decode("utf-8"))

    @property
    def ip(self) -> str:
        """str: The external IP address."""
        return self._ip

    @property
    def country_code(self) -> str:
        """str: The country code of the IP address."""
        return self._country_code

    @property
    def country_name(self) -> str:
        """str: The country name of the IP address."""
        return self._country_name

    @property
    def region_name(self) -> str:
        """str: The region name of the IP address."""
        return self._region_name

    @property
    def city_name(self) -> str:
        """str: The city name of the IP address."""
        return self._city_name

    @property
    def latitude(self) -> str:
        """str: The latitude of the IP address location."""
        return self._latitude

    @property
    def longitude(self) -> str:
        """str: The longitude of the IP address location."""
        return self._longitude

    @property
    def zip_code(self) -> str:
        """str: The ZIP code of the IP address location."""
        return self._zip_code

    @property
    def time_zone(self) -> str:
        """str: The time zone of the IP address location."""
        return self._time_zone

    @property
    def asn(self) -> str:
        """str: The Autonomous System Number of the IP address."""
        return self._asn

    @property
    def as_name(self) -> str:
        """str: The name of the Autonomous System."""
        return self._as_name

    @property
    def is_proxy(self) -> bool:
        """bool: Indicates if the IP address is a proxy."""
        return self._is_proxy


class GeoLoc(InfoGeoloc):
    """Subclass of InfoGeoloc for extended geolocation functionalities."""

    def __init__(self, *args: tuple, **kwrgs: dict) -> None:
        """Initialize GeoLoc with optional arguments.

        Args:
            *args: Variable length argument list.
            **kwrgs: Arbitrary keyword arguments.

        """
