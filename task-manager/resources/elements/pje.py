"""Defina constantes de elementos e URLs utilizados para automação no sistema PJE.

Este módulo fornece:
- URLs de login, consulta e busca do sistema PJE;
- Seletores de elementos para automação de login e busca.

"""

url_login = "https://pje.trt11.jus.br/primeirograu/login.seam"
chk_login = "https://pje.trt11.jus.br/pjekz/painel/usuario-externo"
login_input = 'input[id="username"]'
password_input = 'input[id="password"]'  # noqa: S105
btn_entrar = 'button[id="btnEntrar"]'
url_pautas = "https://pje.trt11.jus.br/consultaprocessual/pautas"
url_busca = "url_de_busca_AC"
btn_busca = "btn_busca_AC"

pattern_url = (
    r"^https:\/\/pje\.trt\d{1,2}\.jus\.br\/consultaprocessual\/detalhe-processo\/"
    r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\/\d+(#[a-zA-Z0-9]+)?$"
)


CSS_FORM_LOGIN = 'form[id="kc-form-login"]'
ID_INPUT_CODIGO_PJE = "pjeoffice-code"
ID_INPUT_DESAFIO = "phrase"

LINK_AUTENTICACAO_SSO = (
    "https://pje.trt{regiao}.jus.br/primeirograu/authenticateSSO.seam"
)
OL_LIST_ANEXOS = '//*[@id="cdk-drop-list-3"]'
XPATH_BTN_ASSINAR = (
    '//*[contains(@aria-label, "Assinar documento e juntar ao processo")]'
)

XPATH_DIALOG_COMPROVANTE = '//*[@id="mat-dialog-6"]/ng-component/div/div[2]'

TAG_LIST_ANEXOS = "pje-item-lista-anexo-pdf"
XPATH_COLUNA_CAMPOS = '//*[contains(@class, "coluna-2")]'
XPATH_INPUT_TIPO_ANEXO = '//*[contains(@aria-label,"Tipo de Documento")]'
XPATH_INPUT_ANEXOS = '//*[@id="upload-anexo-1"]'
XPATH_BTN_TAB_ANEXOS = '//*[@id="mat-tab-label-0-1"]'
XPATH_BTN_ADICIONAR_ADVOGADO = '//*[@id="cdk-step-content-0-2"]/div/pje-habilitacao-advogados-grid/div/mat-card/mat-card-content/pje-data-table/div[1]/table/thead/tr/th[4]/div/div/div/button'
XPATH_SALVA_ARQUIVO = '//*[@id="cdk-step-content-0-3"]/pje-anexar-documento/div/pje-duas-colunas/div/div[1]/form/div/div[1]/button'

LINK_DADOS_BASICOS = "https://pje.trt{trt_id}.jus.br/pje-consulta-api/api/processos/dadosbasicos/{numero_processo}"
LINK_CONSULTA_PROCESSO = "https://pje.trt{trt_id}.jus.br/pje-comum-api/api/processos/id/{id_processo}"
LINK_DOWNLOAD_INTEGRA = "https://pje.trt{trt_id}.jus.br/pje-comum-api/api/processos/id/{id_processo}/documentos/agrupados?processoCompleto=true"
LINK_CONSULTA_PARTES = "https://pje.trt{trt_id}.jus.br/pje-comum-api/api/processos/id/{id_processo}/partes"
LINK_CONSULTA_ASSUNTOS = "https://pje.trt{trt_id}.jus.br/pje-comum-api/api/processos/id/{id_processo}/assuntos"
LINK_AUDIENCIAS = "https://pje.trt{trt_id}.jus.br/pje-comum-api/api/processos/id/{id_processo}/audiencias"
LINK_AUDIENCIAS_CANCELADAS = str(LINK_AUDIENCIAS + "?canceladas=true")
