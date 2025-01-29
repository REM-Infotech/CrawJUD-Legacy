"""
Module for uninstalling certificates.
"""

import subprocess

from tqdm import tqdm


def uninstall(nome_do_certificado: str) -> None:
    """
    Uninstalls a certificate by its name.

    Args:
        nome_do_certificado (str): The name of the certificate to uninstall.

    Raises:
        subprocess.CalledProcessError: If the certificate uninstallation process fails.
    """
    certs = {}
    try:
        comando = ["certutil", "-store", "-user", "my"]
        resultados = subprocess.run(
            comando,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout.splitlines()

        # Encontrando o hash baseado no nome
        hash_certificado = None
        inside_cert = False
        for line in resultados:
            if "================" in line:
                inside_cert = False
            if "Requerente:" in line:
                if nome_do_certificado in line:
                    certs[nome_do_certificado] = ""

                atual_cert = line
                inside_cert = True
            if "Hash Cert(sha1):" in line and inside_cert:
                if nome_do_certificado in atual_cert:
                    hash_certificado = line.split(": ")[1].strip()
                    certs[nome_do_certificado] = hash_certificado
                    break

    except subprocess.CalledProcessError as e:
        # Handle exception
        raise e

    try:
        thumbprint = certs[nome_do_certificado]
        comando = ["certutil", "-delstore", "-user", "my", thumbprint]
        resultado = subprocess.run(
            comando,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        tqdm.write(resultado.stdout, resultado.stderr)

    except subprocess.CalledProcessError as e:
        raise e
