from collections.abc import Sequence
from typing import TYPE_CHECKING, ClassVar, Self, cast

from __types import MyAny, T
from flask import abort
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.pagination import Pagination as FSAPagination
from flask_sqlalchemy.pagination import QueryPagination as FSAQueryPagination
from sqlalchemy import exc as sa_exc
from sqlalchemy.orm import Query as SAQuery
from sqlalchemy.sql._typing import (
    _ColumnExpressionArgument,
    _ColumnsClauseArgument,
)

_Entities = _ColumnsClauseArgument[T] | Sequence[_ColumnsClauseArgument[T]]
if TYPE_CHECKING:
    from ._model import Model


class QueryProperty[T]:
    def __init__(self) -> None:
        pass

    def __get__(self, instance: MyAny, owner: type[T]) -> Query[T]:
        from app import app

        cls = cast("Model", owner)
        if "sqlalchemy" in app.extensions:
            cls.__fsa__ = cast(SQLAlchemy, app.extensions["sqlalchemy"])  # pyright: ignore[reportAttributeAccessIssue]

        _owner = owner

        with app.app_context():
            return Query(cls, cls.__fsa__.session())


class Pagination[T](FSAPagination):
    """Adds typing to Flask-SQLAlchemy's Pagination."""


class QueryPagination[T](FSAQueryPagination):
    """Adds typing to Flask-SQLAlchemy's QueryPagination."""


class Query[T](SAQuery):
    """Dummy class to represent the Query type with a generic parameter."""

    _total: ClassVar[int] = 0

    def len(self) -> int:
        return self._total

    @property
    def total(self) -> int:
        return self._total

    @total.setter
    def total(self, new_total: int) -> None:
        self._total = new_total

    def filter(self, *criterion: _ColumnExpressionArgument) -> Self:
        return super().filter(*criterion)

    def filter_by(self, **kwargs: MyAny) -> Self:
        return super().filter_by(**kwargs)

    def first(self) -> T | None:
        self._total = 1
        return super().first()

    def all(self) -> list[T]:
        all_results = super().all()
        self._total = len(all_results)

        return all_results

    def get_or_404(self, ident: MyAny, description: str | None = None) -> T:
        """Results or 404.

        Like :meth:`~sqlalchemy.orm.Query.get`
            but aborts with a ``404 Not Found``
            error instead of returning ``None``.

        :param ident: The primary key to query.
        :param description: A custom message to show on the error page.

        Returns:
            The instance corresponding to the given primary key, or raises a 404 error.

        """
        rv = self.get(ident)

        if rv is None:
            abort(404, description=description)

        self._total = 1
        return rv

    def first_or_404(self, description: str | None = None) -> T:
        """First or 404.

        Like :meth:`~sqlalchemy.orm.Query.first` but aborts with a ``404 Not Found``
        error instead of returning ``None``.

        :param description: A custom message to show on the error page.

        Returns:
            The first result of the query, or raises a 404 error if no results are found

        """
        rv = self.first()

        if rv is None:
            abort(404, description=description)

        self._total = 1
        return rv

    def one_or_404(self, description: str | None = None) -> T:
        """One or 404.

        Like :meth:`~sqlalchemy.orm.Query.one` but aborts with a ``404 Not Found``
        error instead of raising ``NoResultFound`` or ``MultipleResultsFound``.

        :param description: A custom message to show on the error page.

        Returns:
            The one and only result of the query, or raises a 404 error if the result
            is not exactly one.

        """
        try:
            self._total = 1
            return self.one()
        except (sa_exc.NoResultFound, sa_exc.MultipleResultsFound):
            abort(404, description=description)

    def paginate(
        self,
        *,
        page: int | None = None,
        per_page: int | None = None,
        max_per_page: int | None = None,
        error_out: bool = True,
        count: bool = True,
    ) -> QueryPagination[T]:
        """Paginate the query.

        Apply an offset and limit to the query based on the current page and number
        of items per page, returning a :class:`.Pagination` object.

        :param page: The current page, used to calculate the offset. Defaults to the
            ``page`` query arg during a request, or 1 otherwise.
        :param per_page: The maximum number of items on a page, used to calculate the
            offset and limit. Defaults to the ``per_page`` query arg during a request,
            or 20 otherwise.
        :param max_per_page: The maximum allowed value for ``per_page``, to limit a
            user-provided value. Use ``None`` for no limit. Defaults to 100.
        :param error_out: Abort with a ``404 Not Found`` error if no items are returned
            and ``page`` is not 1, or if ``page`` or ``per_page`` is less than 1, or if
            either are not ints.
        :param count: Calculate the total number of values by issuing an extra count
            query. For very complex queries this may be inaccurate or slow, so it can be
            disabled and set manually if necessary.

        .. versionchanged:: 3.0
            All parameters are keyword-only.

        .. versionchanged:: 3.0
            The ``count`` query is more efficient.

        .. versionchanged:: 3.0
            ``max_per_page`` defaults to 100.

        Returns:
            A :class:`.Pagination` object containing the results for the specified page.

        """
        return cast(
            QueryPagination[Self],
            QueryPagination(
                query=self,
                page=page,
                per_page=per_page,
                max_per_page=max_per_page,
                error_out=error_out,
                count=count,
            ),
        )
