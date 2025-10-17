"""Gerencia tarefas e execução de chamados CSI para automação judicial.

Este módulo define a classe Chamados, responsável por orquestrar tarefas
automatizadas relacionadas a chamados CSI, utilizando integração com bots,
tratamento de contexto e execução assíncrona de tarefas.

"""

from time import sleep

from __types import AnyType
from dotenv import load_dotenv
from resources.elements import csi as el
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm

from .master import CsiBot

load_dotenv()


class Chamados(CsiBot):
    """Gerencia chamados CSI para execução de tarefas automatizadas.

    Herda de CsiBot e implementa métodos de execução de chamados.
    """

    def execution(self, *args: AnyType, **kwargs: AnyType) -> None:
        tqdm.write("OK")

        frame = self.frame

        calls = {
            "Solicitação de Subsídios para Contestação": self.solicitacao_subsidios,
        }
        self.driver.maximize_window()

        for pos, item in tqdm(enumerate(frame)):
            self.bot_data = item
            self.row = pos + 1

            func = calls[item["NOME_EVENTO"]]
            func()

        self.driver.quit()

    def solicitacao_subsidios(self) -> None:
        try:
            driver = self.driver
            wait = WebDriverWait(driver, 10)
            data = self.bot_data
            driver.get(el.url_solicitacao_subsidios)
            frame_questionario = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.iframe_questionario,
                )),
            )

            driver.switch_to.frame(frame_questionario)
            campo_nome_reclamante = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    el.campo_nome_reclamante_subsidios,
                )),
            )

            documentos = [
                "CONTRACHEQUES MAIO/2023 - JULHO/2023",
                "CONTRATO 2023",
                "FERIAS",
            ]

            docs_with_dot = [f" •  {doc}" for doc in documentos]

            documentos_formatado = "\n".join(docs_with_dot)

            campo_nome_reclamante.send_keys(self.bot_data["AUTOR"])
            driver.switch_to.default_content()

            desc = el.desc_subsidios.format(
                ATO="ATORD",
                NUMERO_PROCESSO=data["NUMERO_PROCESSO"],
                COMARCA_VARA=f"{data['NÚMERO_SIGLA_OJ']} {data.get('JUÍZO', '')}",
                ASSUNTOS=f" -  {data.get('FATO_GERADOR', 'Diversos')}",
                NOME_RECLAMANTE=data["AUTOR"],
                CPF_RECLAMANTE=data.get("CPF_AUTOR", "000.000.000-00"),
                RECLAMADO=data["RÉU"],
                TIMESET=self.saudacao(),
                DOCUMENTOS=documentos_formatado,
                NOME_SOLICITANTE=data["RESPONSAVEL_PROCESSO"],
            )

            campo_desc = driver.find_element(
                By.CSS_SELECTOR,
                el.campo_desc_subsidios,
            )
            campo_desc.send_keys(desc)

            sleep(10)

        except Exception as e:
            tqdm.write(str(e))
