"""Módulo do decorator CrossDomain."""

from __future__ import annotations

from datetime import timedelta
from functools import wraps
from typing import TYPE_CHECKING

from flask import (
    Response,
    abort,
    current_app,
    make_response,
    request,
)

from __types import MyAny

if TYPE_CHECKING:
    from collections.abc import Callable

    from __types import Methods, P


class CrossDomain:
    """Adicione cabeçalhos CORS às respostas HTTP para permitir requisições cross-origin.

    Esta classe fornece métodos utilitários para normalizar métodos, cabeçalhos, origens
    e tempo de cache, além de um decorador para aplicar as regras CORS em rotas HTTP.
    """

    def __init__(
        self,
        origin: str | None = None,
        methods: list[Methods] | None = None,
        headers: list[str] | None = None,
        max_age: int = 21600,
        *,
        attach_to_all: bool = True,
        automatic_options: bool = True,
    ) -> None:
        """Inicializa o objeto CrossDomain com configurações de CORS personalizadas.

        Args:
            origin (str | None): Origem permitida para requisições CORS.
            methods (Methods | None): Métodos HTTP permitidos.
            headers (list[str] | None): Lista de cabeçalhos permitidos.
            max_age (int): Tempo máximo de cache dos cabeçalhos CORS em segundos.
            attach_to_all (bool): Se deve anexar cabeçalhos a todas as respostas.
            automatic_options (bool): Se deve gerar resposta automática para OPTIONS.

        """
        self.origin = origin
        self.methods = methods
        self.headers = headers
        self.max_age = 21600
        self.attach_to_all = attach_to_all
        self.automatic_options = automatic_options
        self.current_request_method = None

    def __call__[T](
        self,
        wrapped_function: Callable[P, T],
    ) -> Callable[P, Response]:
        """Adiciona cabeçalhos CORS à resposta HTTP.

        Args:
            wrapped_function (Callable[P, T]): Função a ser decorada para receber os
                cabeçalhos CORS.
            origin (str | None): Origem permitida para CORS.
            methods (list[str] | None): Métodos HTTP permitidos.
            headers (list[str] | None): Cabeçalhos permitidos.
            max_age (int): Tempo máximo de cache dos cabeçalhos CORS.
            attach_to_all (bool): Se deve anexar cabeçalhos a todas respostas.
            automatic_options (bool): Se deve gerar resposta automática para OPTIONS.

        Returns:
            Callable: Decorador que adiciona cabeçalhos CORS à resposta.

        """
        _normalized_methods = self._normalize_methods(self.methods)
        _normalized_headers = self._normalize_headers(self.headers)
        _normalized_origin = self._normalize_origin(self.origin)
        _normalized_max_age = self._normalize_max_age(self.max_age)

        @wraps(wrapped_function)
        def _wrapped(
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> Response:
            _kwarg = kwargs
            _args = args
            self.current_request_method = request.method
            if request.method == "GET":
                resp = self._handle_request(
                    wrapped_function,
                    *args,
                    **kwargs,
                )

            elif self.automatic_options and request.method == "OPTIONS":
                resp = self._handle_options()
            elif request.method == "POST":
                resp = self._handle_request(
                    wrapped_function,
                    *args,
                    **kwargs,
                )
            else:
                abort(405)  # Method Not Allowed

            if not self.attach_to_all and request.method != "OPTIONS":
                return resp

            return resp

        return _wrapped

    def _normalize_methods(
        self,
        methods: list[Methods] | None,
    ) -> str | None:
        """Normaliza os métodos HTTP para cabeçalho CORS.

        Args:
            methods (list[str] | None): Lista de métodos HTTP ou None.

        Returns:
            str | None: Métodos HTTP normalizados em string ou None.

        """
        return (
            ", ".join(sorted(x.upper() for x in methods))
            if methods
            else None
        )

    def _normalize_headers(
        self,
        headers: list[str] | None,
    ) -> str | None:
        """Normaliza os cabeçalhos para CORS.

        Args:
            headers (list[str] | None): Lista de cabeçalhos HTTP ou None.

        Returns:
            str | None: Cabeçalhos normalizados em string ou None.

        """
        if headers is not None:
            return ", ".join(x.upper() for x in headers)
        return None

    def _normalize_origin(self, origin: str | None) -> str | None:
        """Normaliza a origem para CORS.

        Args:
            origin (str | None): Origem permitida para CORS.

        Returns:
            str | None: Origem normalizada como string ou None.

        """
        if isinstance(origin, str):
            return origin
        if origin:
            return ", ".join(origin)
        return None

    def _normalize_max_age(self, max_age: int | timedelta) -> int:
        """Normaliza o tempo máximo de cache para CORS.

        Args:
            max_age (int | timedelta): Tempo máximo de cache em segundos ou timedelta.

        Returns:
            int: Tempo máximo de cache em segundos.

        """
        return (
            int(max_age.total_seconds())
            if isinstance(max_age, timedelta)
            else max_age
        )

    def _get_methods(self, normalized_methods: str | None) -> str:
        """Obtém os métodos permitidos para CORS.

        Returns:
            str: Métodos HTTP permitidos, formatados para cabeçalho CORS.

        """
        if normalized_methods is not None:
            return normalized_methods
        options_resp = current_app.make_default_options_response()
        return options_resp.headers["allow"]

    def _handle_options(self) -> Response:
        """Gera resposta para método OPTIONS.

        Returns:
            Response: Resposta padrão para o método OPTIONS.

        """
        return current_app.make_default_options_response()

    def _handle_request(
        self,
        f: Callable,
        *args: MyAny,
        **kwargs: MyAny,
    ) -> Response:
        """Processa requisição com verificação de XSRF.

        Returns:
            Response: Resposta HTTP gerada após o processamento da requisição.

        """
        name_ = f.__globals__.get("__name__")
        if name_ == "flask_jwt_extended.view_decorators":
            cookie_xsrf_name = current_app.config.get(
                "JWT_ACCESS_CSRF_COOKIE_NAME",
            )
            header_xsrf_name = current_app.config.get(
                "JWT_ACCESS_CSRF_HEADER_NAME",
                "X-Xsrf-Token",
            )
            xsrf_token = None
            if isinstance(cookie_xsrf_name, str):
                xsrf_token = request.cookies.get(cookie_xsrf_name, None)
            if not xsrf_token and self.current_request_method != "GET":
                abort(401, description="Missing XSRF Token")

            else:
                request.headers.environ.update({
                    f"HTTP_{header_xsrf_name.replace('-', '_')}".upper(): xsrf_token,
                })
        return make_response(f(*args, **kwargs))

    def _set_cors_headers(
        self,
        resp: Response,
        normalized_origin: str | None,
        normalized_methods: str | None,
        normalized_headers: str | None,
        normalized_max_age: int,
    ) -> None:
        """Define os cabeçalhos CORS na resposta."""
        h = resp.headers

        methods = self._get_methods(normalized_methods)
        h["Access-Control-Allow-Origin"] = normalized_origin
        h["Access-Control-Allow-Methods"] = methods
        h["Access-Control-Max-Age"] = str(normalized_max_age)
        if normalized_headers is not None:
            h["Access-Control-Allow-Headers"] = normalized_headers
