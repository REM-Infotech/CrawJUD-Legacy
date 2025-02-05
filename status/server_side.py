"""Module for server-side operations in CrawJUD-Bots."""

from typing import Dict, List

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis_flask import Redis

from status import SetStatus


def load_cache(pid: str, app: Flask) -> Dict[str, str]:
    """Load cache data for a given PID from Redis.

    Args:
        pid (str): The process ID for which to load the cache.
        app (Flask): The Flask application instance.

    Returns:
        Dict[str, str]: A dictionary containing cached log data.

    """
    log_pid: Dict[str, str | int] = {}
    list_cached: List[Dict[str, str | int]] = []

    redis_client: Redis = app.extensions["redis"]
    redis_key = f"*{pid}*"

    get_cache: List | None = redis_client.keys(redis_key)
    if get_cache:
        list_cache: List[str] = list(get_cache)
        for cache in list_cache:
            k_process, k_pid, k_pos, k_value = cache.split(":")
            cached = [{"pid": k_pid, "pos": int(k_value)}]
            list_cached.extend(cached)

        sorted_cache: List[Dict[str, str | int]] = sorted(list_cached, key=lambda x: x.get("pos"), reverse=True)

        for item in sorted_cache:
            pos = item["pos"]
            redis_key = f"process:{pid}:pos:{pos}"
            logs_pid = redis_client.hgetall(redis_key)

            log_pid = dict(logs_pid)

    return log_pid


def FormatMessage(data: Dict[str, str | int] = None, pid: str = None, app: Flask = None) -> Dict[str, str | int]:  # noqa: C901, N802
    """Format and update the status message for a given process.

    This function interacts with a SQLAlchemy database and a Redis client to
    manage and update the status of a process identified by a PID. It ensures
    that the process status is correctly initialized and updated in Redis,
    and it updates the provided data dictionary with the latest status
    information.

    Args:
        data (Dict[str, str | int], optional): A dictionary containing process
            information. Defaults to an empty dictionary.
        pid (str, optional): The process ID. Defaults to None.
        app (Flask, optional): The Flask application instance, used to access
            extensions like SQLAlchemy and Redis. Defaults to None.

    Returns:
        Dict[str, str | int]: The updated data dictionary with the latest
        process status information.

    Raises:
        Exception: If any error occurs during the process, the original data
        dictionary is returned without modifications.

    """
    if data is None:
        data = {}
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        redis_client: Redis = app.extensions["redis"]

        data_type = data.get("type", "success")
        data_graphic = data.get("graphicMode", "doughnut")
        data_message = data.get("message", "Finalizado")
        data_system = data.get("system", "vazio")
        data_pid = data.get("pid", "vazio")
        data_pos = data.get("pos", 0)

        # Verificar informações obrigatórias
        chk_infos = [data.get("system"), data.get("typebot")]
        if all(chk_infos):
            SetStatus(
                status="Finalizado",
                pid=pid,
                system=data_system,
                typebot=data_system,
            ).botstop(db, app)

        # Chave única para o processo no Redis
        redis_key = f"process:{data_pid}:pos:{data_pos}"

        # Carregar dados do processo do Redis
        log_pid = redis_client.hgetall(redis_key)

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
        elif data_pos > 0 or data["message"] != log_pid["message"] or "pid" not in data:
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

            type_S1 = data_type == "success"  # noqa: N806
            type_S2 = data_type == "info"  # noqa: N806
            type_S3 = data_graphic != "doughnut"  # noqa: N806

            typeSuccess = type_S1 or type_S2 and type_S3  # noqa: N806

            log_pid["pos"] = data_pos

            if typeSuccess:
                if log_pid.get("remaining") and log_pid.get("success"):
                    log_pid["remaining"] = int(log_pid["remaining"]) - 1
                    if "fim da execução" not in data_message.lower():
                        log_pid["success"] = int(log_pid["success"]) + 1

            elif data_type == "error":
                log_pid.update({"remaining": int(log_pid["remaining"]) - 1})  # pragma: no cover
                log_pid.update({"errors": int(log_pid["errors"]) + 1})  # pragma: no cover

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
            }
        )

    except Exception:
        data = data

    return data


# def StatusStop(pid: str):

#     from app import db
#     from app.models import Executions

#     execut = db.session.query(Executions).filter(Executions.pid == pid).first()
#     if not execut:
#         execut = False

#     elif execut:
#         execut = str(execut.status) != "Em Execução"

#     return execut


# def stopped_bot(pid: str):

#     from app.models import CacheLogs

#     checks = []
#     log_pid = CacheLogs.query.filter(CacheLogs.pid == pid).first()
#     check1 = log_pid is not None
#     checks.append(check1)
#     if check1:
#         check2 = str(log_pid.status) == "Finalizado"
#         checks.append(check2)

#     allchecks = all(checks)
#     return allchecks
