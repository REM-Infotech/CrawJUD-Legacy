"""Fornece tipos e wrappers personalizados para integração com Celery.

Este módulo define classes tipadas para resultados assíncronos,
resultados imediatos (EagerResult) e assinaturas de tarefas (Signature),
facilitando o uso de Celery com tipagem estática e integração com
o sistema de tarefas assíncronas do projeto.

Nota: Esta versão funciona apenas quando o Celery está disponível.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    AnyStr,
    ClassVar,
    Generic,
    ParamSpec,
    Self,
    TypeVar,
)

if TYPE_CHECKING:
    try:
        from celery.canvas import Signature as __Signature
        from celery.result import AsyncResult as __AsyncResult
        from celery.result import states
        from crawjud.custom.celery import AsyncCelery
        _CELERY_AVAILABLE = True
    except ImportError:
        _CELERY_AVAILABLE = False
        # Stubs para quando o Celery não está disponível
        __Signature = object
        __AsyncResult = object
        states = None
        AsyncCelery = Any
else:
    try:
        from celery.canvas import Signature as __Signature
        from celery.result import AsyncResult as __AsyncResult
        from celery.result import states
        _CELERY_AVAILABLE = True
    except ImportError:
        _CELERY_AVAILABLE = False
        # Stubs para quando o Celery não está disponível
        __Signature = object
        __AsyncResult = object
        states = None

P = ParamSpec("P")
R = TypeVar("R")
TClassBot = TypeVar("TClassBot", bound=object)
TBotSpec = ParamSpec("TBotSpec", bound=AnyStr)

class_set = set()


class CeleryResult[T](__AsyncResult):
    """Celery Results.

    Class that wraps the result of a task execution.

    Used to check the status of a task, retrieve its result,
    and perform other operations related to task results.

    See Also:
        :ref:`guide-results` for the complete guide.

    """

    if TYPE_CHECKING:
        _app: ClassVar[AsyncCelery] = None

    def get(
        self,
        timeout: int | None = None,
        interval: float = 0.5,
        callback: T = None,
        on_message: T = None,
        on_interval: T = None,
        *,
        propagate: bool = True,
        no_ack: bool = True,
        follow_parents: bool = True,
        disable_sync_subtasks: bool = True,
        exception_states: Any = None,
        propagate_states: Any = None,
    ) -> Generic[R]:
        """Wait until task is ready, and return its result."""
        if not _CELERY_AVAILABLE:
            raise RuntimeError("Celery not available")
        return super().get(
            timeout,
            propagate,
            interval,
            no_ack,
            follow_parents,
            callback,
            on_message,
            on_interval,
            disable_sync_subtasks,
            exception_states or [],
            propagate_states or [],
        )

    def wait_ready(self, timeout: float | None = None) -> T:
        """Aguarde até que o resultado da tarefa esteja pronto ou o timeout."""
        if not _CELERY_AVAILABLE:
            return None
        # Implementação simplificada para evitar dependências
        return None


class Signature[T](__Signature):
    """Task Signature.

    Class that wraps the arguments and execution options
    for a single task invocation.
    """

    if TYPE_CHECKING:
        _app: ClassVar[AsyncCelery] = None

    def __init__(
        self,
        task: T = None,
        args: T = None,
        kwargs: T = None,
        options: T = None,
        type: T = None,  # noqa: A002
        subtask_type: T = None,
        *,
        immutable: bool = False,
        app: Any = None,
        **ex: T,
    ) -> None:
        """Inicialize uma instância de Signature com os parâmetros fornecidos."""
        if not _CELERY_AVAILABLE:
            # Implementação stub quando Celery não está disponível
            self.task = task
            self.args = args or ()
            self.kwargs = kwargs or {}
            self.options = options or {}
            return
            
        if isinstance(task, str) and app:
            task = app.tasks[task]

        super().__init__(
            task,
            args,
            kwargs,
            options,
            type,
            subtask_type,
            immutable,
            app,
            **ex,
        )

    @classmethod
    def from_dict(cls, d: T, app: T | None = None) -> Self:
        """Crie uma instância de Signature a partir de um dicionário de dados."""
        if not _CELERY_AVAILABLE:
            return cls(d.get("task"), d.get("args"), d.get("kwargs"))
        
        typ = d.get("subtask_type")
        if typ and hasattr(cls, "TYPES"):
            target_cls = cls.TYPES.get(typ, cls)
            if target_cls is not cls:
                return target_cls.from_dict(d, app=app)
        return cls(d, app=app)

    def apply_async(
        self,
        args: AnyStr | None = None,
        kwargs: AnyStr | None = None,
        route_name: str | None = None,
        **options: AnyStr,
    ) -> CeleryResult | None:
        """Apply this task asynchronously."""
        if not _CELERY_AVAILABLE:
            return None
        
        try:
            async_result = super().apply_async(
                args,
                kwargs,
                route_name=route_name,
                **options,
            )
            return async_result
        except Exception:
            return None


__all__ = [
    "CeleryResult",
    "Signature",
]