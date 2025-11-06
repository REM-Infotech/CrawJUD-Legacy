"""Define elementos e seletores utilizados para automação no sistema Projudi.

Este módulo contém variáveis com URLs, seletores CSS e XPath para facilitar
operações automatizadas de login, busca de processos, navegação e manipulação
de documentos no Projudi.

"""

URL_LOGIN = "https://csi.infraero.gov.br/citsmart/webmvc/login"
URL_BUSCA_CHAMADO = "https://csi.infraero.gov.br/citsmart/pages/pesquisaSolicitacoesServicos/pesquisaSolicitacoesServicos.load"
URL_CONFIRMA_LOGIN = (
    "https://csi.infraero.gov.br/citsmart/pages/smartPortal/smartPortal.load"
)

XPATH_CAMPO_USERNAME = '//input[@id="user_login"]'
XPATH_CAMPO_SENHA = '//input[@id="password"]'
XPATH_BTN_ENTRAR = '//button[@id="btnEntrar"]'
XPATH_INPUT_NUMERO_CHAMADO = '//input[@id="idSolicitacaoServicoPesquisa"]'
XPATH_BTN_BUSCAR = '//*[@id="form"]/div/div/div[1]/div[2]/div[9]/div/button[@name="btnPesquisar"]'
XPATH_TABLE_SOLICITACOES = '//div[@id="tabelaSolicitacoes"]/div/table/tbody'
XPATH_DIV_POPUP_ANEXOS = '//div[@id="POPUP_menuAnexos"]'

XPATH_IFRAME_ANEXOS = '//iframe[@name="fraUpload_uploadAnexos"]'

COMMAND_ANEXOS = "anexos({NUMERO_CHAMADO})"
