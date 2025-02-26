"""Module for dashboard routes.

This module provides endpoints for rendering the dashboard and for serving
chart data for executions per month and most executed bots.
"""

import json
import locale
import os
import pathlib
from collections import Counter
from datetime import datetime

import pandas as pd
from deep_translator import GoogleTranslator
from quart import Blueprint, Response, abort, jsonify, make_response, render_template, request, session

from crawjud_bots.web import db
from crawjud_bots.web.decorators import login_required
from crawjud_bots.web.models import Executions, LicensesUsers, SuperUser, Users

translator = GoogleTranslator(source="en", target="pt")

path_static = os.path.join(pathlib.Path(__file__).parent.resolve(), "static")
path_template = os.path.join(pathlib.Path(__file__).parent.resolve(), "templates")

dash = Blueprint("dash", __name__, template_folder=path_template, static_folder=path_static)


@dash.route("/dashboard", methods=["GET"])
@login_required
async def dashboard() -> Response:
    """Render the dashboard page with execution data.

    Returns:
        Response: A Quart response rendering the dashboard.

    """
    title = "Dashboard"
    page = "dashboard.html"

    user = Users.query.filter(Users.login == session["login"]).first()
    user_id = user.id

    chksupersu = db.session.query(SuperUser).join(Users).filter(Users.id == user_id).first()

    executions = db.session.query(Executions)
    if not chksupersu:
        executions = executions.join(LicensesUsers).filter_by(license_token=user.licenseusr.license_token)

        chk_admin = db.session.query(LicensesUsers).join(LicensesUsers.admins).filter(Users.id == user_id).first()

        if not chk_admin:
            executions = executions.join(Users).filter(Users.id == user_id)

    database = executions.all()

    return await make_response(
        await render_template(
            "index.html",
            page=page,
            title=title,
            database=database,
        ),
    )


@dash.route("/PerMonth", methods=["GET"])
@login_required
async def month_chart() -> Response:
    """Return JSON data representing execution counts per month.

    Returns:
        Response: A Quart JSON response containing labels and values.

    """
    if not session.get("license_token"):
        abort(405, description="Sessão expirada. Faça login novamente.")

    # Define a localidade para português do Brasil
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")

    chart_data = {"labels": [], "values": []}  # Preenche com 0 se o mês estiver ausente

    admin_cookie = request.cookies.get("roles_admin")
    supersu_cookie = request.cookies.get("roles_supersu")

    if supersu_cookie and json.loads(supersu_cookie).get("login_id") == session["_id"]:
        query_result = Executions.query.all()

    elif admin_cookie and json.loads(admin_cookie).get("login_id") == session["_id"]:
        query_result = (
            db.session.query(Executions)
            .join(LicensesUsers)
            .filter(LicensesUsers.license_token == session["license_token"])
            .all()
        )

    elif not supersu_cookie or not admin_cookie:
        query_result = db.session.query(Executions).join(Users).filter(Users.login == session["login"]).all()

    # Extrai o mês de cada data de execução em português
    if query_result:
        meses = []
        current_year = datetime.now().year
        for execut in query_result:
            execution_date = execut.data_execucao
            if execution_date and execution_date.year == current_year:
                # Converte para o nome do mês em português
                mes_nome = execution_date.date().strftime("%B").lower()
                meses.append(mes_nome)

        # Conta as ocorrências de cada mês
        execucoes_por_mes = Counter(meses)

        # Lista completa de meses em português para garantir que todos os meses estejam representados
        all_months = [
            "janeiro",
            "fevereiro",
            "março",
            "abril",
            "maio",
            "junho",
            "julho",
            "agosto",
            "setembro",
            "outubro",
            "novembro",
            "dezembro",
        ]

        # Garante que todos os meses estejam na contagem, mesmo que com valor 0
        chart_data = {
            "labels": all_months,
            "values": [
                execucoes_por_mes.get(month, 0) for month in all_months
            ],  # Preenche com 0 se o mês estiver ausente
        }

    # Retorna para o template
    return await make_response(
        jsonify(
            chart_data,
        ),
    )


@dash.route("/most_executed", methods=["GET"])
@login_required
async def most_executed() -> Response:
    """Return JSON data of the most executed bots.

    Returns:
        Response: A Quart JSON response with bot names and execution counts.

    """
    if not session.get("license_token"):
        abort(405, description="Sessão expirada. Faça login novamente.")

    # Executa a query para obter todos os registros
    admin_cookie = request.cookies.get("roles_admin")
    supersu_cookie = request.cookies.get("roles_supersu")

    chart_data = {"labels": [], "values": []}

    if supersu_cookie and json.loads(supersu_cookie).get("login_id") == session["_id"]:
        query_result = Executions.query.all()

    elif admin_cookie and json.loads(admin_cookie).get("login_id") == session["_id"]:
        query_result = (
            db.session.query(Executions)
            .join(LicensesUsers)
            .filter(LicensesUsers.license_token == session["license_token"])
            .all()
        )

    elif not supersu_cookie or not admin_cookie:
        query_result = db.session.query(Executions).join(Users).filter(Users.login == session["login"]).all()

    if query_result:
        # Converte o query result para uma lista de dicionários
        data = [{"bot_name": execut.bot.display_name} for execut in query_result]

        # Cria o DataFrame a partir da lista de dicionários
        df = pd.DataFrame(data)

        # Agrupando pelo nome do bot e contando as execuções totais
        execucoes_por_bot = df["bot_name"].value_counts().reset_index()
        execucoes_por_bot.columns = ["bot_name", "count"]

        # Preparando dados para o Chart.js
        chart_data = {
            "labels": execucoes_por_bot["bot_name"].tolist(),
            "values": execucoes_por_bot["count"].tolist(),
        }

    # Retorna para o template
    return await make_response(
        jsonify(
            chart_data,
        ),
    )
