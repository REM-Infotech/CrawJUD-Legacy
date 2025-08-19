"""Define elementos e seletores utilizados para automação no sistema Projudi.

Este módulo contém variáveis com URLs, seletores CSS e XPath para facilitar
operações automatizadas de login, busca de processos, navegação e manipulação
de documentos no Projudi.

"""

from __future__ import annotations

url_busca = ""

url_login = "https://csi.infraero.gov.br/citsmart/webmvc/login"

campo_username: str = 'input[id="user_login"]'
campo_passkey: str = 'input[id="password"]'

btn_entrar: str = 'button[id="btnEntrar"]'
url_logado: str = (
    "https://csi.infraero.gov.br/citsmart/pages/smartPortal/smartPortal.load"
)

# Subsidios
url_solicitacao_subsidios = "https://csi.infraero.gov.br/citsmart/pages/smartPortal/smartPortal.load#/atividade/251/7232/7233"


iframe_questionario = 'iframe[id="questionario"]'
campo_nome_reclamante_subsidios = "input[id='campoDyn_7287']"

campo_desc_subsidios = 'textarea[id="solicitacaoObservacao"]'

desc_subsidios = """
PROCESSO {ATO} {NUMERO_PROCESSO}
{COMARCA_VARA}

ASSUNTO(S):
{ASSUNTOS}

RECLAMANTE: {NOME_RECLAMANTE} CPF: {CPF_RECLAMANTE}
RECLAMADO: {RECLAMADO}


Prezados, {TIMESET}!
Solicito os seguintes documentos para subsidiar a contestação:
{DOCUMENTOS}

Atenciosamente,
{NOME_SOLICITANTE}

"""
