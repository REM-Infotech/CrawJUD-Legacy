"""Define elementos e seletores utilizados para automação no sistema Projudi.

Este módulo contém variáveis com URLs, seletores CSS e XPath para facilitar
operações automatizadas de login, busca de processos, navegação e manipulação
de documentos no Projudi.

"""

from __future__ import annotations

URL_LOGIN = "https://csi.infraero.gov.br/citsmart/webmvc/login"
URL_BUSCA_CHAMADO = "https://csi.infraero.gov.br/citsmart/pages/pesquisaSolicitacoesServicos/pesquisaSolicitacoesServicos.load"
URL_CONFIRMA_LOGIN = (
    "https://csi.infraero.gov.br/citsmart/pages/smartPortal/smartPortal.load"
)

XPATH_CAMPO_USERNAME = '//input[@id="user_login"]'
XPATH_CAMPO_SENHA = '//input[@id="password"]'
XPATH_BTN_ENTRAR = '//button[@id="btnEntrar"]'
