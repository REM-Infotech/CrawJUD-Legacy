from .properties import Configuracao


class PJE_AM(Configuracao):
    url_login: str = "https://pje.trt11.jus.br/primeirograu/login.seam"
    chk_login: str = "https://pje.trt11.jus.br/pjekz/painel/usuario-externo"

    login_input: str = 'input[id="username"]'
    password_input: str = 'input[id="password"]'
    btn_entrar: str = 'button[id="btnEntrar"]'
    url_pautas: str = "https://pje.trt11.jus.br/consultaprocessual/pautas"

    url_busca: str = "url_de_busca_AC"
    btn_busca: str = "btn_busca_AC"
