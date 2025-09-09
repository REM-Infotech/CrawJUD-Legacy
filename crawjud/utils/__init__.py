"""Módulo de Utilitários - Ferramentas e Funções Auxiliares.

Este módulo contém utilitários e ferramentas auxiliares utilizadas em todo o 
sistema CrawJUD. Fornece funcionalidades de suporte para automação web, 
gerenciamento de processos, logging, armazenamento e outras operações comuns.

Principais funcionalidades:
    - Gerenciamento de processos WebDriver
    - Finalização de processos relacionados ao BrowserMob Proxy
    - Finalização de processos ChromeDriver órfãos
    - Utilitários para limpeza de recursos

Submodulos principais:
    - logger: Sistema de logging estruturado
    - storage: Gerenciamento de armazenamento e arquivos
    - webdriver: Configuração e gerenciamento do Selenium WebDriver
    - xlsx_generator: Geração de planilhas e relatórios
    - formatadores: Formatação de dados brasileiros (CPF, CNPJ, etc.)
    - recaptcha: Integração com serviços de resolução de captcha

Exemplo de uso:
    >>> from crawjud.utils import kill_chromedriver, kill_browsermob
    >>> 
    >>> # Limpeza de processos órfãos
    >>> kill_chromedriver()
    >>> kill_browsermob()

Funções principais:
    - kill_browsermob(): Finaliza processos do BrowserMob Proxy
    - kill_chromedriver(): Finaliza processos do ChromeDriver
"""

from __future__ import annotations

from contextlib import suppress

import psutil
from tqdm import tqdm


def kill_browsermob() -> None:
    """Finaliza processos relacionados ao BrowserMob Proxy."""
    keyword = "browsermob"
    matching_procs = []

    # Primeira fase: coleta segura dos processos
    list_process_iter = list(
        filter(
            lambda p: "cmdline" in p.info
            and p.info["cmdline"] is not None
            and len(p.info["cmdline"]) > 0,
            psutil.process_iter(["pid", "name", "cmdline"]),
        ),
    )

    for proc in list_process_iter:
        with suppress(
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
            Exception,
        ):
            if any(
                keyword in part
                for part in proc.info["cmdline"]
                if proc.info["cmdline"] is not None
            ):
                matching_procs.append(proc)

    # Segunda fase: finalização dos processos encontrados
    for proc in matching_procs:
        with suppress(psutil.NoSuchProcess, psutil.AccessDenied, Exception):
            tqdm.write(
                f"Matando PID {proc.pid} ({' '.join(proc.info['cmdline'])})",
            )
            proc.kill()


def kill_chromedriver() -> None:
    """Finaliza processos relacionados ao ChromeDriver."""
    keyword = "chromedriver"
    matching_procs = []
    list_process_iter = list(
        filter(
            lambda p: "cmdline" in p.info
            and p.info["cmdline"] is not None
            and len(p.info["cmdline"]) > 0,
            psutil.process_iter(["pid", "name", "cmdline"]),
        ),
    )
    # Primeira fase: coleta segura dos processos
    for proc in list_process_iter:
        with suppress(
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
            Exception,
        ):
            if any(
                keyword in part
                for part in proc.info["cmdline"]
                if proc.info["cmdline"] is not None
            ):
                matching_procs.append(proc)

    # Segunda fase: finalização dos processos encontrados
    for proc in matching_procs:
        with suppress(psutil.NoSuchProcess, psutil.AccessDenied, Exception):
            tqdm.write(
                f"Matando PID {proc.pid} ({' '.join(proc.info['cmdline'])})",
            )
            proc.kill()
