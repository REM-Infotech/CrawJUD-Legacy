from flask import Flask

from redis_flask import Redis
from status import SetStatus


def load_cache(pid: str, app: Flask):

    log_pid: dict[str, str | int] = {}
    list_cached: list[dict[str, str | int]] = []

    redis_client: Redis = app.extensions["redis"]
    redis_key = f"*{pid}*"

    get_cache: list | None = redis_client.keys(redis_key)
    if get_cache:

        list_cache: list[str] = list(get_cache)
        for cache in list_cache:
            k_process, k_pid, k_pos, k_value = cache.split(":")
            cached = [{"pid": k_pid, "pos": int(k_value)}]

            list_cached.extend(cached)

        get_cache: list[dict[str, str | int]] = sorted(
            list_cached, key=lambda x: x.get("pos"), reverse=True
        )

        for item in get_cache:

            pos = item["pos"]
            redis_key = f"process:{pid}:pos:{pos}"
            logs_pid = redis_client.hgetall(redis_key)

            log_pid = dict(logs_pid)

            if "total" not in log_pid:
                continue

            if "last_log" in log_pid:
                log_pid.update({"message": log_pid.get("last_log")})
                log_pid.pop("last_log")

            break

    return log_pid


def serverSide(data: dict[str, str], pid: str, app: Flask):

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
        ).botstop()

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
    elif data_pos > 0 or data["message"] != log_pid["message"]:

        if not log_pid:

            if data_pos == data_pos + 2:
                data_pos -= 1

            if data_pos > 1:
                # Chave única para o processo no Redis
                redis_key_tmp = f"process:{data_pid}:pos:{data_pos - 1}"

                # Carregar dados do processo do Redis
                log_pid = redis_client.hgetall(redis_key_tmp)

            elif data_pos == 1:
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

        type_S1 = data_type == "success"
        type_S2 = data_type == "info"
        type_S3 = data_graphic != "doughnut"

        typeSuccess = type_S1 or type_S2 and type_S3

        log_pid["pos"] = data_pos

        if typeSuccess:

            if log_pid.get("remaining") and log_pid.get("success"):

                log_pid["remaining"] = int(log_pid["remaining"]) - 1
                if "fim da execução" not in data_message.lower():
                    log_pid["success"] = int(log_pid["success"]) + 1

        elif data_type == "error":
            log_pid["remaining"] = int(log_pid["remaining"]) - 1
            log_pid["errors"] = int(log_pid["errors"]) + 1
            if data_pos == 0:
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

    return data


def StatusStop(pid: str):

    from app import db
    from app.models import Executions

    execut = db.session.query(Executions).filter(Executions.pid == pid).first()
    if not execut:
        execut = False

    elif execut:
        execut = str(execut.status) != "Em Execução"

    return execut


def stopped_bot(pid: str):

    from app.models import CacheLogs

    checks = []
    log_pid = CacheLogs.query.filter(CacheLogs.pid == pid).first()
    check1 = log_pid is not None
    checks.append(check1)
    if check1:
        check2 = str(log_pid.status) == "Finalizado"
        checks.append(check2)

    allchecks = all(checks)
    return allchecks
