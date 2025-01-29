# Usar uma imagem base do Windows com suporte ao Python
FROM python:3.13.1-windowsservercore-ltsc2022

# Configurações básicas de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR C:/crawjudbot_app

# Copiar arquivos do projeto
COPY windows/inst_vnc.ps1 C:/crawjudbot_app/

RUN powershell.exe -noexit ".\inst_vnc.ps1"

# RUN powershell.exe -noexit ".\inst_postgres.ps1"
RUN pip install --no-cache-dir poetry
RUN git config --global --add safe.directory C:/crawjudbot_app
RUN poetry config virtualenvs.create false; poetry install --without dev


