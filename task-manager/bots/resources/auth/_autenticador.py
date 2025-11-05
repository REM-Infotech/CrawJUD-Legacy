"""Empty."""

import base64
import secrets
from pathlib import Path
from uuid import uuid4

import jpype
import requests
from app.types import StrPath
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    pkcs12,
)
from cryptography.x509 import Certificate

# Importa classes Java
from jpype import JArray, JByte, JClass

if not jpype.isJVMStarted():
    jpype.startJVM()


ByteArrayInputStream = JClass("java.io.ByteArrayInputStream")
CertificateFactory = JClass("java.security.cert.CertificateFactory")
ArrayList = JClass("java.util.ArrayList")


class AutenticadorPJe:
    def __init__(
        self,
        bytes_ou_caminho_cert: bytes | StrPath,
        senha_certificado: bytes | str,
    ) -> None:
        bytes_cert = bytes_ou_caminho_cert
        if isinstance(bytes_ou_caminho_cert, (str, Path)):
            with Path(bytes_ou_caminho_cert).open("rb") as fp:
                bytes_cert = fp.read()

        if isinstance(senha_certificado, str):
            senha_certificado = bytes(senha_certificado, encoding="utf8")

        tuple_load_pkcs12 = pkcs12.load_key_and_certificates(
            bytes_cert, senha_certificado
        )

        self.key = tuple_load_pkcs12[0]
        self.cert = tuple_load_pkcs12[1]
        self._chain = [self.cert]
        self._chain.extend(tuple_load_pkcs12[2])
        self.alg_map = {
            "SHA256withRSA": hashes.SHA256(),
            "SHA1withRSA": hashes.SHA1(),  # noqa: S303
            "MD5withRSA": hashes.MD5(),  # noqa: S303
        }

    def assinar(self, valor: bytes | str) -> None:
        if isinstance(valor, str):
            valor = valor.encode()

        digest = self.alg_map.get("MD5withRSA")
        if not digest:
            raise ValueError("Algoritmo não suportado: " + "MD5withRSA")

        self._assinatura = self.key.sign(valor, padding.PKCS1v15(), digest)

        return self

    @property
    def assinatura_base64(self) -> str | None:
        if self._assinatura:
            return base64.b64encode(self._assinatura).decode()

        return None

    @property
    def cadeia_certificado_b64(self) -> str | None:
        if self._chain:
            return self.generate_pkipath_java(self._chain)

        return None

    def random_base36(self) -> str:
        # Gera um número aleatório de 52 bits (mesma entropia de Math.random)
        n = secrets.randbits(52)
        chars = "0123456789abcdefghijklmnopqrstuvwxyz"
        s = ""
        while n:
            n, r = divmod(n, 36)
            s = chars[r] + s
        return "0." + s or "0.0"

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

        if resp.status_code == 204:
            return desafio, uuid_tarefa

        return None, None

    def generate_pkipath_java(self, cert_chain: list[Certificate]) -> str:
        """Gera um PKIPath (DER e Base64) chamando o código Java nativo via JPype.

        cert_chain: lista de x509.Certificate (cryptography)

        Returns:
            Uma tupla contendo os bytes do PKIPath (DER) e sua representação em Base64.

        """
        cf = CertificateFactory.getInstance("X.509")
        java_chain = ArrayList()

        for cert in cert_chain:
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
