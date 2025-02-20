"""Handle server-side operations for bot status tracking and caching with Redis integration."""

import logging

import redis.commands.search.aggregation as aggregations
import redis.commands.search.reducers as reducers
import redis.exceptions
from flask_sqlalchemy import SQLAlchemy
from quart import Quart
from redis.commands.json.path import Path  # noqa: F401
from redis.commands.search.field import NumericField, TagField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from plugins import Redis


class LogsManager:
    """Handle server-side operations for bot status tracking and caching with Redis integration."""

    model_data: dict[str, str | int] = {
        "pid": "A1B2C3",
        "pos": 0,
        "total": 0,
        "remaining": 0,
        "success": 0,
        "errors": 0,
        "status": "Em Execução",
        "message": "vazio",
        "graphicMode": "doughnut",
        "system": "vazio",
        "typebot": "vazio",
    }

    schema = (
        TagField("$.system", as_name="system"),
        TextField("$.typebot", as_name="typebot"),
        TextField("$.pid", as_name="pid"),
        NumericField("$.pos", as_name="pos"),
        NumericField("$.total", as_name="total"),
        NumericField("$.remaining", as_name="remaining"),
        NumericField("$.success", as_name="success"),
        NumericField("$.errors", as_name="errors"),
        TextField("$.status", as_name="status"),
        TextField("$.message", as_name="message"),
        TextField("$.graphicMode", as_name="graphicMode"),
    )

    def create_index(self, r: Redis, pid: str) -> None:
        """Create a search index for Redisearch."""
        index_created = r.ft("idx:execution:%s" % pid).create_index(
            self.schema,
            definition=IndexDefinition(
                prefix=["execution:%s:" % pid],
                index_type=IndexType.JSON,
            ),
        )

        return index_created

    async def load_cache(self, pid: str, app: Quart = None, client: Redis = None) -> dict[str, str]:
        """Load cache data for a given PID from Redis.

        Args:
            pid (str): The process ID for which to load the cache.
            app (Quart): The Quart application instance.
            client (Redis): The Redis client instance.

        Returns:
            dict[str, str]: A dictionary containing cached log data.

        """
        log_pid: dict[str, str | int] = {}
        list_cached: list[dict[str, str | int]] = []
        redis_client: Redis = client

        if client is None:
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

    async def format_message_log(  # noqa: C901
        self,
        data: dict[str, str | int] = None,
        pid: str = None,
        app: Quart = None,
        client: Redis = None,
    ) -> dict[str, str | int]:  # noqa: C901, N802
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
            client (Redis, optional): The Redis client instance. Defaults to None.


        Returns:
            dict[str, str | int]: The updated data dictionary with the latest
            process status information.

        Raises:
            Exception: If any error occurs during the process, the original data
            dictionary is returned without modifications.

        """
        if data is None:
            data = self.model_data

        try:
            if client is None:
                client: Redis = app.extensions["redis"]

            querylog = client.ft("idx:executions:%s" % pid).search(Query("@pid:%s" % pid))  # noqa: F841

            message = data.get("type")  # noqa: F841

            self.create_index(client, pid)

            dataset = {
                "pid": data.get("pid", "A1B2C3"),
                "status": data.get("status", "Em Execução"),
                "graphicMode": data.get("graphicMode", "doughnut"),
                "system": data.get("system", "vazio"),
                "typebot": data.get("typebot", "vazio"),
                "total": data.get("total", 0),
                "remaining": data.get("remaining", 0),
                "success": data.get("success", 0),
                "errors": data.get("errors", 0),
            }

            mesageset = {
                "message": data.get("message", "vazio"),
                "pos": data.get("pos", 0),
            }

            client.json().set("execution:%s" % pid, Path.root_path(), dataset)
            client.json().set("execution:%s:%d" % (pid, int(data.get("pos"))), Path.root_path(), mesageset)

        except Exception as e:
            if app is not None:
                app.logger.error("An error occurred: %s", str(e))

            else:
                logging.getLogger(__name__).error("An error occurred: %s", str(e))

        return data

        # try:
        #     db: SQLAlchemy = app.extensions["sqlalchemy"]  # noqa: F841
        #     redis_client: Redis = app.extensions["redis"]

        #     data_type = data.get("type", "success")
        #     data_graphic = data.get("graphicMode", "doughnut")
        #     data_message = data.get("message", "Finalizado")
        #     data_system = data.get("system", "vazio")  # noqa: F841
        #     data_pid = data.get("pid", "vazio")
        #     data_pos = data.get("pos", 0)

        #     # Verificar informações obrigatórias
        #     chk_infos = [data.get("system"), data.get("typebot")]  # noqa: F841
        #     if all(chk_infos) or data_message.split("> ")[-1].islower():
        #         async with app.app_context():
        #             await TaskExec.task_exec(data_bot=data, exec_type="stop", app=app)

        #     # Chave única para o processo no Redis
        #     redis_key = f"process:{data_pid}:pos:{data_pos}"
        #     redis_client.set()
        #     # Carregar dados do processo do Redis
        #     log_pid = await redis_client.hgetall(redis_key)

        #     # Caso não exista, inicializar o registro
        #     if not log_pid and int(data_pos) == 0:
        #         log_pid = {
        #             "pid": data_pid,
        #             "pos": data_pos,
        #             "total": data.get("total", 100),  # Defina um valor padrão ou ajuste
        #             "remaining": data.get("total", 100),  # Igual ao total no início
        #             "success": 0,
        #             "errors": 0,
        #             "status": "Iniciado",
        #             "message": data_message,
        #         }
        #         redis_client.hset(redis_key, mapping=log_pid)
        #         redis_client.set

        #     # Atualizar informações existentes
        #     elif int(data_pos) > 0 or data_message != log_pid["message"] or "pid" not in data:
        #         if not log_pid or "pid" not in data:
        #             if data_pos > 1:
        #                 # Chave única para o processo no Redis
        #                 redis_key_tmp = f"process:{data_pid}:pos:{data_pos - 1}"

        #                 # Carregar dados do processo do Redis
        #                 log_pid = redis_client.hgetall(redis_key_tmp)
        #                 if not log_pid:
        #                     redis_key_tmp = f"process:{data_pid}:pos:{data_pos - 2}"
        #                     log_pid = redis_client.hgetall(redis_key_tmp)
        #                     if not log_pid:
        #                         log_pid = {
        #                             "pid": data_pid,
        #                             "pos": data_pos,
        #                             "total": data.get("total", 100),
        #                             "remaining": data.get("total", 100),
        #                             "success": 0,
        #                             "errors": 0,
        #                             "status": "Iniciado",
        #                             "message": data_message,
        #                         }

        #             elif data_pos == 1:
        #                 log_pid = {
        #                     "pid": data_pid,
        #                     "pos": data_pos,
        #                     "total": data.get("total", 100),
        #                     "remaining": data.get("total", 100),
        #                     "success": 0,
        #                     "errors": 0,
        #                     "status": "Iniciado",
        #                     "message": data_message,
        #                 }

        #         type_s1 = data_type == "success"  # noqa: N806
        #         type_s2 = data_type == "info"  # noqa: N806
        #         type_s3 = data_graphic != "doughnut"  # noqa: N806

        #         type_success = type_s1 or (type_s2 and type_s3)  # noqa: N806

        #         log_pid["pos"] = data_pos

        #         if type_success:
        #             if log_pid.get("remaining") and log_pid.get("success"):
        #                 log_pid["remaining"] = int(log_pid["remaining"]) - 1
        #                 if "fim da execução" not in data_message.lower():
        #                     log_pid["success"] = int(log_pid["success"]) + 1

        #         elif data_type == "error":
        #             log_pid.update({"remaining": int(log_pid["remaining"]) - 1})
        #             log_pid.update({"errors": int(log_pid["errors"]) + 1})

        #             if data_pos == 0 or app.testing:
        #                 log_pid["errors"] = log_pid["total"]
        #                 log_pid["remaining"] = 0

        #         log_pid["message"] = data_message
        #         redis_client.hset(redis_key, mapping=log_pid)

        #     # Atualizar o dicionário de saída
        #     data.update(
        #         {
        #             "pid": log_pid["pid"],
        #             "pos": log_pid["pos"],
        #             "total": log_pid["total"],
        #             "remaining": log_pid["remaining"],
        #             "success": log_pid["success"],
        #             "errors": log_pid["errors"],
        #             "status": log_pid["status"],
        #             "message": log_pid["message"],
        #         },
        #     )

        # except Exception as e:
        #     app.logger.error("An error occurred: %s", str(e))
        #     data = data

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


format_message_log = LogsManager().format_message_log
load_cache = LogsManager().load_cache
