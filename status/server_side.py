from status import SetStatus


def serverSide(data: dict[str, str], pid: str):

    from app import app, db
    from app.models import CacheLogs, Executions

    data_type = data.get("type", "success")
    data_graphic = data.get("graphicMode", "doughnut")
    data_message = data.get("message", "Finalizado")
    data_system = data.get("system", "vazio")
    data_pid = data.get("pid", "vazio")
    data_pos = data.get("pos", 0)

    with app.app_context():
        chk_infos = [data.get("system"), data.get("typebot")]

        if all(chk_infos):

            SetStatus(
                status="Finalizado",
                pid=pid,
                system=data_system,
                typebot=data_system,
            ).botstop()

        log_pid = CacheLogs.query.filter(CacheLogs.pid == data_pid).first()
        if not log_pid:

            execut = (
                db.session.query(Executions).filter(Executions.pid == data_pid).first()
            )
            log_pid = CacheLogs(
                pid=data_pid,
                pos=data_pos,
                total=int(execut.total_rows) - 1,
                remaining=int(execut.total_rows) - 1,
                success=0,
                errors=0,
                status=execut.status,
                last_log=data_message,
            )
            db.session.add(log_pid)

        elif log_pid:

            log_pid.pos = data_pos

            type_S1 = data_type == "success"
            type_S2 = data_type == "info"
            type_S3 = data_graphic != "doughnut"

            typeSuccess = type_S1 or type_S2 and type_S3

            if typeSuccess:

                log_pid.remaining -= 1
                if "fim da execução" not in data_message.lower():
                    log_pid.success += 1

                log_pid.last_log = data_message

            elif data_type == "error":

                log_pid.remaining -= 1
                log_pid.errors += 1
                log_pid.last_log = data_message

                if data_pos == 0:
                    log_pid.errors = log_pid.total
                    log_pid.remaining = 0

        db.session.commit()
        data.update(
            {
                "pid": data_pid,
                "pos": data_pos,
                "total": log_pid.total,
                "remaining": log_pid.remaining,
                "success": log_pid.success,
                "errors": log_pid.errors,
                "status": log_pid.status,
                "last_log": log_pid.last_log,
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
