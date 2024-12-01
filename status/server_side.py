from status import SetStatus


def serverSide(data: dict[str, str], pid: str):
    from app import redis_client

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
    redis_key = f"process:{data_pid}"

    # Carregar dados do processo do Redis
    log_pid = redis_client.hgetall(redis_key)

    # Caso não exista, inicializar o registro
    if not log_pid:
        log_pid = {
            "pid": data_pid,
            "pos": data_pos,
            "total": data.get("total", 100),  # Defina um valor padrão ou ajuste
            "remaining": data.get("total", 100),  # Igual ao total no início
            "success": 0,
            "errors": 0,
            "status": "Iniciado",
            "last_log": data_message,
        }
        redis_client.hset(redis_key, mapping=log_pid)

    # Atualizar informações existentes
    else:
        log_pid["pos"] = data_pos
        if data_type in ["success", "info"] and data_graphic != "doughnut":
            log_pid["remaining"] = int(log_pid["remaining"]) - 1
            log_pid["success"] = int(log_pid["success"]) + 1
        elif data_type == "error":
            log_pid["remaining"] = int(log_pid["remaining"]) - 1
            log_pid["errors"] = int(log_pid["errors"]) + 1
            if data_pos == 0:
                log_pid["errors"] = log_pid["total"]
                log_pid["remaining"] = 0

        log_pid["last_log"] = data_message
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
            "last_log": log_pid["last_log"],
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
