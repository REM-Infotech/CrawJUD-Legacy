"""Handle server-side operations for bot status tracking and caching with Redis integration."""

from flask_sqlalchemy import SQLAlchemy
from quart import Quart
from redis_flask import Redis


async def load_cache(pid: str, app: Quart) -> dict[str, str]:
    """Load cache data for a given PID from Redis.

    Args:
        pid (str): The process ID for which to load the cache.
        app (Quart): The Quart application instance.

    Returns:
        dict[str, str]: A dictionary containing cached log data.

    """
    log_pid: dict[str, str | int] = {}
    list_cached: list[dict[str, str | int]] = []

    redis_client: Redis = app.extensions["redis"]
    redis_key = f"*{pid}*"

    get_cache: list | None = redis_client.keys(redis_key)
    if get_cache:
        list_cache: list[str] = list(get_cache)
        for cache in list_cache:
            _, k_pid, __, k_value = cache.split(":")
            cached = [{"pid": k_pid, "pos": int(k_value)}]
            list_cached.extend(cached)

        sorted_cache: list[dict[str, str | int]] = sorted(list_cached, key=lambda x: x.get("pos"), reverse=True)

        for item in sorted_cache:
            pos = item["pos"]
            redis_key = f"process:{pid}:pos:{pos}"
            logs_pid = redis_client.hgetall(redis_key)

            log_pid = dict(logs_pid)

    return log_pid


async def format_message_log(
    data: dict[str, str | int] = None,
    pid: str = None,
    app: Quart = None,
) -> dict[str, str | int]:
    """Format and update the status message for a given process.

    This function interacts with a SQLAlchemy database and a Redis client to
    manage and update the status of a process identified by a PID. It ensures
    that the process status is correctly initialized and updated in Redis,
    and it updates the provided data dictionary with the latest status
    information.

    Args:
        data (dict[str, str | int], optional): A dictionary containing process
            information. Defaults to an empty dictionary.
        pid (str, optional): The process ID. Defaults to None.
        app (Flask, optional): The Quart application instance, used to access
            extensions like SQLAlchemy and Redis. Defaults to None.


    Returns:
        dict[str, str | int]: The updated data dictionary with the latest
        process status information.

    Raises:
        Exception: If any error occurs during the process, the original data
        dictionary is returned without modifications.

    """
    from crawjud.utils import TaskExec

    if data is None:
        data = {}
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]  # noqa: F841
        redis_client: Redis = app.extensions["redis"]

        data_type = data.get("type", "success")
        data_graphic = data.get("graphicMode", "doughnut")
        data_message = data.get("message", "Finalizado")
        data_system = data.get("system", "vazio")  # noqa: F841
        data_pid = data.get("pid", "vazio")
        data_pos = data.get("pos", 0)

        # Verificar informações obrigatórias
        chk_infos = [data.get("system"), data.get("typebot")]
        if all(chk_infos) or data_message.split("> ")[-1].islower():
            async with app.app_context():
                await TaskExec.task_exec(data_bot=data, exec_type="stop", app=app)

        # Chave única para o processo no Redis
        redis_key = f"process:{data_pid}:pos:{data_pos}"

        # Carregar dados do processo do Redis
        log_pid = redis_client.hgetall(redis_key)

        log_pid = {key.decode(): value.decode() for key, value in log_pid.items()}

        # Caso não exista, inicializar o registro
        if not log_pid and int(data_pos) == 0:
            log_pid = {
                "pid": data_pid,
                "pos": data_pos,
                "total": data.get("total", 100),  # Defina um valor padrão ou ajuste
                "remaining": data.get("total", 100),  # Igual ao total no início
                "success": 0,
                "errors": 0,
                "status": "Iniciado",
                "message": data_message,
            }
            redis_client.hset(redis_key, mapping=log_pid)

        # Atualizar informações existentes
        elif int(data_pos) > 0 or data_message != log_pid["message"] or "pid" not in data:
            if not log_pid or "pid" not in data:
                if data_pos > 1:
                    # Chave única para o processo no Redis
                    redis_key_tmp = f"process:{data_pid}:pos:{data_pos - 1}"

                    # Carregar dados do processo do Redis
                    log_pid = redis_client.hgetall(redis_key_tmp)
                    if not log_pid:
                        redis_key_tmp = f"process:{data_pid}:pos:{data_pos - 2}"
                        log_pid = redis_client.hgetall(redis_key_tmp)
                        if not log_pid:
                            log_pid = {
                                "pid": data_pid,
                                "pos": data_pos,
                                "total": data.get("total", 100),
                                "remaining": data.get("total", 100),
                                "success": 0,
                                "errors": 0,
                                "status": "Iniciado",
                                "message": data_message,
                            }

                elif data_pos == 1:
                    log_pid = {
                        "pid": data_pid,
                        "pos": data_pos,
                        "total": data.get("total", 100),
                        "remaining": data.get("total", 100),
                        "success": 0,
                        "errors": 0,
                        "status": "Iniciado",
                        "message": data_message,
                    }

            type_s1 = data_type == "success"
            type_s2 = data_type == "info"
            type_s3 = data_graphic != "doughnut"

            type_success = type_s1 or (type_s2 and type_s3)

            log_pid["pos"] = data_pos

            if type_success:
                if log_pid.get("remaining") and log_pid.get("success"):
                    log_pid["remaining"] = int(log_pid["remaining"]) - 1
                    if "fim da execução" not in data_message.lower():
                        log_pid["success"] = int(log_pid["success"]) + 1

            elif data_type == "error":
                log_pid.update({"remaining": int(log_pid["remaining"]) - 1})
                log_pid.update({"errors": int(log_pid["errors"]) + 1})

                if data_pos == 0 or app.testing:
                    log_pid["errors"] = log_pid["total"]
                    log_pid["remaining"] = 0

            log_pid["message"] = data_message
            redis_client.hset(redis_key, mapping=log_pid)

        # Atualizar o dicionário de saída
        data.update(
            {
                "pid": log_pid["pid"],
                "pos": log_pid["pos"],
                "total": log_pid["total"],
                "remaining": log_pid["remaining"],
                "success": log_pid["success"],
                "errors": log_pid["errors"],
                "status": log_pid["status"],
                "message": log_pid["message"],
            },
        )

    except Exception as e:
        app.logger.error("An error occurred: %s", str(e))
        data = data

    return data


# def StatusStop(pid: str):

#     from crawjud.api import db
#     from crawjud.api.models import Executions

#     execut = db.session.query(Executions).filter(Executions.pid == pid).first()
#     if not execut:
#         execut = False

#     elif execut:
#         execut = str(execut.status) != "Em Execução"

#     return execut


# def stopped_bot(pid: str):

#     from crawjud.api.models import CacheLogs

#     checks = []
#     log_pid = CacheLogs.query.filter(CacheLogs.pid == pid).first()
#     check1 = log_pid is not None
#     checks.append(check1)
#     if check1:
#         check2 = str(log_pid.status) == "Finalizado"
#         checks.append(check2)

#     allchecks = all(checks)
#     return allchecks
