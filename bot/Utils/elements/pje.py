"""This module provides the PJE_AM class for automating PJE-AM operations."""

from .properties import Configuracao


class PJE_AM(Configuracao):
    """Handle authentication, navigation, and interactions with the PJE-AM system.

    Attributes:
        url_login (str): The login URL for PJE-AM.
        chk_login (str): The URL to check if login was successful.
        login_input (str): The CSS selector for the username input field.
        password_input (str): The CSS selector for the password input field.
        btn_entrar (str): The CSS selector for the login button.
        url_pautas (str): The URL for accessing the pautas page.
        url_busca (str): A placeholder URL for busca operations.
        btn_busca (str): The selector for the busca button.
    """

    url_login: str = "https://pje.trt11.jus.br/primeirograu/login.seam"
    chk_login: str = "https://pje.trt11.jus.br/pjekz/painel/usuario-externo"

    login_input: str = 'input[id="username"]'
    password_input: str = 'input[id="password"]'
    btn_entrar: str = 'button[id="btnEntrar"]'
    url_pautas: str = "https://pje.trt11.jus.br/consultaprocessual/pautas"

    url_busca: str = "url_de_busca_AC"
    btn_busca: str = "btn_busca_AC"
