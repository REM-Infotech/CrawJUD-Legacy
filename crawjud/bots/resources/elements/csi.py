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
