"""Defina constantes de elementos e URLs utilizados para automação no sistema PJE.

Este módulo fornece:
- URLs de login, consulta e busca do sistema PJE;
- Seletores de elementos para automação de login e busca.

"""

url_login: str = "https://pje.trt11.jus.br/primeirograu/login.seam"
chk_login: str = "https://pje.trt11.jus.br/pjekz/painel/usuario-externo"
login_input: str = 'input[id="username"]'
password_input: str = 'input[id="password"]'  # noqa: S105
btn_entrar: str = 'button[id="btnEntrar"]'
url_pautas: str = "https://pje.trt11.jus.br/consultaprocessual/pautas"
url_busca: str = "url_de_busca_AC"
btn_busca: str = "btn_busca_AC"

pattern_url = (
    r"^https:\/\/pje\.trt\d{1,2}\.jus\.br\/consultaprocessual\/detalhe-processo\/"
    r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\/\d+(#[a-zA-Z0-9]+)?$"
)

LINK_DADOS_BASICOS = "https://pje.trt{trt_id}.jus.br/pje-consulta-api/api/processos/dadosbasicos/{numero_processo}"
LINK_CONSULTA_PROCESSO = "https://pje.trt{trt_id}.jus.br/pje-comum-api/api/processos/id/{id_processo}"
LINK_DOWNLOAD_INTEGRA = "https://pje.trt{trt_id}.jus.br/pje-comum-api/api/processos/id/{id_processo}/documentos/agrupados?processoCompleto=true"
LINK_CONSULTA_PARTES = "https://pje.trt{trt_id}.jus.br/pje-comum-api/api/processos/id/{id_processo}/partes"
LINK_CONSULTA_ASSUNTOS = "https://pje.trt{trtid}.jus.br/pje-comum-api/api/processos/id/{id_processo}/assuntos"
LINK_AUDIENCIAS = "https://pje.trt{trt_id}.jus.br/pje-comum-api/api/processos/id/{id_processo}/audiencias"

LINK_AUDIENCIAS_CANCELADAS = str(LINK_AUDIENCIAS + "?canceladas=true")
