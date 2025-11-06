import base64
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

import jpype
import pyotp
import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import (
    Encoding,
)
from cryptography.hazmat.primitives.serialization.pkcs12 import load_pkcs12

# Importa classes Java
from jpype import JArray, JByte, JClass
from pykeepass import PyKeePass
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
)
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from bots.resources.auth._main import AutenticadorBot
from bots.resources.elements import pje as el
from common import auth_error
from constants import NO_CONTENT_STATUS

if TYPE_CHECKING:
    from cryptography.x509 import Certificate

    from bots.controller.pje import PjeBot

if not jpype.isJVMStarted():
    jpype.startJVM()


ByteArrayInputStream = JClass("java.io.ByteArrayInputStream")
CertificateFactory = JClass("java.security.cert.CertificateFactory")
ArrayList = JClass("java.util.ArrayList")


class AutenticadorPJe(AutenticadorBot):
    _chain: list[Certificate]

    def __init__(self, bot: PjeBot) -> None:
        path_certificado = Path(environ.get("CERTIFICADO_PFX"))
        senha_certificado = environ.get("CERTIFICADO_PASSWORD").encode()
        with path_certificado.open("rb") as fp:
            bytes_cert = fp.read()

        tuple_load_pkcs12 = load_pkcs12(bytes_cert, senha_certificado)

        self.key = tuple_load_pkcs12.key
        self.cert = tuple_load_pkcs12.cert
        self._chain = [self.cert]
        self._chain.extend(tuple_load_pkcs12.additional_certs)
        self.alg_map = {
            "SHA256withRSA": hashes.SHA256(),
            "SHA1withRSA": hashes.SHA1(),  # noqa: S303
            "MD5withRSA": hashes.MD5(),  # noqa: S303
        }

        super().__init__(bot=bot)

    def __call__(self) -> bool:
        try:
            url = el.LINK_AUTENTICACAO_SSO.format(regiao=self.regiao)
            self.driver.get(url)

            if "https://sso.cloud.pje.jus.br/" not in self.driver.current_url:
                return True
            self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.CSS_FORM_LOGIN,
                )),
            )

            autenticado = self.autenticar()
            if not autenticado:
                auth_error()

            desafio = autenticado[0]
            uuid_sessao = autenticado[1]

            self.driver.execute_script(
                el.COMMAND,
                el.ID_INPUT_DESAFIO,
                desafio,
            )
            self.driver.execute_script(
                el.COMMAND,
                el.ID_CODIGO_PJE,
                uuid_sessao,
            )

            self.driver.execute_script("document.forms[0].submit()")

            otp_uri = _get_otp_uri()
            otp = str(pyotp.parse_uri(uri=otp_uri).now())

            input_otp = WebDriverWait(self.driver, 60).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'input[id="otp"]',
                )),
            )

            input_otp.send_keys(otp)
            input_otp.send_keys(Keys.ENTER)

            WebDriverWait(
                driver=self.driver,
                timeout=10,
                poll_frequency=0.3,
                ignored_exceptions=(UnexpectedAlertPresentException),
            ).until(ec.url_contains("pjekz"))

        except Exception:
            self.print_message(
                message="Erro ao realizar autenticação",
                message_type="error",
            )
            return False

        return True

    def assinar(self, valor: bytes | str) -> None:
        if isinstance(valor, str):
            valor = valor.encode()

        digest = self.alg_map.get("MD5withRSA")
        if not digest:
            raise ValueError("Algoritmo não suportado: " + "MD5withRSA")

        self._assinatura = self.key.sign(
            valor,
            padding.PKCS1v15(),
            digest,
        )

        return self

    @property
    def assinatura_base64(self) -> str | None:
        if self._assinatura:
            return base64.b64encode(self._assinatura).decode()

        return None

    @property
    def cadeia_certificado_b64(self) -> str | None:
        if self._chain:
            return self.generate_pkipath_java()

        return None

    def autenticar(self) -> tuple[str, str] | None:
        # enviar diretamente ao endpoint PJe (exemplo)
        desafio = self.random_base36()
        self.assinar(desafio)
        uuid_tarefa = str(uuid4())
        ssopayload = {
            "uuid": uuid_tarefa,
            "mensagem": desafio,
            "assinatura": self.assinatura_base64,
            "certChain": self.cadeia_certificado_b64,
        }

        endpoint = "https://sso.cloud.pje.jus.br/auth/realms/pje/pjeoffice-rest"
        resp = requests.post(endpoint, json=ssopayload, timeout=30)

        if resp.status_code == NO_CONTENT_STATUS:
            return desafio, uuid_tarefa

        return None, None

    def generate_pkipath_java(self) -> str:
        """Gera um PKIPath (DER e Base64) chamando o código Java nativo via JPype.

        cert_chain: lista de x509.Certificate (cryptography)

        Returns:
            Uma tupla contendo os bytes do PKIPath (DER) e sua representação em Base64.

        """
        cf = CertificateFactory.getInstance("X.509")
        java_chain = ArrayList()

        for cert in self._chain:
            # converte o certificado DER em InputStream Java
            der = cert.public_bytes(Encoding.DER)
            der_array = JArray(JByte)(der)
            bais = ByteArrayInputStream(der_array)
            java_cert = cf.generateCertificate(bais)
            java_chain.add(java_cert)

        # gera o CertPath e exporta em formato PkiPath
        cert_path = cf.generateCertPath(java_chain)
        pkipath_bytes = cert_path.getEncoded("PkiPath")

        return base64.b64encode(bytes(pkipath_bytes)).decode("utf-8")


def _get_otp_uri() -> str:
    file_db = str(Path(environ.get("KBDX_PATH")))
    file_pw = environ.get("KBDX_PASSWORD")
    kp = PyKeePass(filename=file_db, password=file_pw)

    return kp.find_entries(
        otp=".*",
        url="https://sso.cloud.pje.jus.br/",
        regex=True,
        first=True,
    ).otp
