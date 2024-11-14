from app import app, db

from status import SetStatus
from app.models import CacheLogs, Executions


def serverSide(data: dict[str, str], pid: str):

    with app.app_context():
        chk_infos = [data.get("system"), data.get("typebot")]

        if all(chk_infos):

            SetStatus(
                status="Finalizado",
                pid=pid,
                system=data["system"],
                typebot=data["system"],
            ).botstop()

        log_pid = CacheLogs.query.filter(CacheLogs.pid == data["pid"]).first()
        if not log_pid:

            execut = (
                db.session.query(Executions)
                .filter(Executions.pid == data["pid"])
                .first()
            )
            log_pid = CacheLogs(
                pid=data["pid"],
                pos=int(data.get("pos", 0)),
                total=int(execut.total_rows) - 1,
                remaining=int(execut.total_rows) - 1,
                success=0,
                errors=0,
                status=execut.status,
                last_log=data.get("message", None),
            )
            db.session.add(log_pid)

        elif log_pid:

            log_pid.pos = int(data.get("pos", 0))

            type_S1 = data["type"] == "success"
            type_S2 = data["type"] == "info"
            type_S3 = data["graphicMode"] != "doughnut"

            typeSuccess = type_S1 or type_S2 and type_S3

            if typeSuccess:

                log_pid.remaining -= 1
                if "fim da execução" not in data["message"].lower():
                    log_pid.success += 1

                log_pid.last_log = data["message"]

            elif data["type"] == "error":

                log_pid.remaining -= 1
                log_pid.errors += 1
                log_pid.last_log = data["message"]

                if data["pos"] == 0:
                    log_pid.errors = log_pid.total
                    log_pid.remaining = 0

        db.session.commit()
        data.update(
            {
                "pid": data["pid"],
                "pos": int(data.get("pos", 0)),
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

    execut = db.session.query(Executions).filter(Executions.pid == pid).first()
    if not execut:
        execut = False

    elif execut:
        execut = str(execut.status) != "Em Execução"

    return execut


def stopped_bot(pid: str):

    checks = []
    log_pid = CacheLogs.query.filter(CacheLogs.pid == pid).first()
    check1 = log_pid is not None
    checks.append(check1)
    if check1:
        check2 = str(log_pid.status) == "Finalizado"
        checks.append(check2)

    allchecks = all(checks)
    return allchecks
