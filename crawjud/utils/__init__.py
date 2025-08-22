"""Utilitários gerais do CrawJUD."""

from __future__ import annotations

from contextlib import suppress

import psutil
from tqdm import tqdm


def kill_browsermob() -> None:
    """Finaliza processos relacionados ao BrowserMob Proxy."""
    keyword = "browsermob"
    matching_procs = []

    # Primeira fase: coleta segura dos processos
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
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

    # Primeira fase: coleta segura dos processos
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
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
