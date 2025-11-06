"""Gerencie o protocolo de petições no sistema JusBr de forma automatizada.

Este módulo contém a classe Protocolo, responsável por executar o fluxo de
protocolo de petições judiciais utilizando automação com Selenium, incluindo
seleção de tipo de protocolo, upload de documentos e tratamento de erros.

"""

from time import sleep

import dotenv
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from app.controllers.pje import PjeBot
from app.resources.elements import pje as el
from app.resources.formatadores import formata_string

dotenv.load_dotenv()


class HabilitiacaoPJe(PjeBot):
    """Controle de funções de Protocolo de Habilitação de processos PJe."""

    def protocolar_habilitacao(
        self,
        bot_data: dict,
        regiao: str,
    ) -> None:
        link_habilitacao = (
            f"https://pje.trt{regiao}.jus.br/pjekz/habilitacao-autos"
        )
        self.driver.get(link_habilitacao)
        self.bot_data = bot_data

        self.__busca_processo()
        self.__selecionar_parte()
        self.__selecionar_parte()
        self.__peticao_principal()
        if bot_data.get("ANEXOS"):
            self.__anexos_peticao()

        self.__assinar_salvar_comprovante()

    def __busca_processo(self) -> None:
        wait = WebDriverWait(self.driver, 5)
        bot_data = self.bot_data

        xpath_busca_processo0 = '//*[@id="mat-input-0"]'
        xpath_busca_processo1 = '//*[@id="mat-input-1"]'

        try:
            campo_busca_processo = wait.until(
                ec.presence_of_element_located((
                    By.XPATH,
                    xpath_busca_processo0,
                )),
            )

        except (TimeoutException, Exception):
            campo_busca_processo = wait.until(
                ec.presence_of_element_located((
                    By.XPATH,
                    xpath_busca_processo1,
                )),
            )

        campo_busca_processo.send_keys(bot_data["NUMERO_PROCESSO"])
        sleep(0.5)
        campo_busca_processo.send_keys(Keys.ENTER)
        sleep(0.5)

        xpath_btn_prosseguir = (
            '//*[@id="area-cadastro"]/mat-action-row/div[2]/button'
        )

        btn_prosseguir = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                xpath_btn_prosseguir,
            )),
        )
        sleep(0.5)

        btn_prosseguir.click()

    def __selecionar_parte(self) -> None:
        tag_tables_pje = "pje-habilitacao-partes-grid"

        bot_data = self.bot_data
        wait = WebDriverWait(self.driver, 10)
        sleep(0.5)
        partes_grid = wait.until(
            ec.presence_of_all_elements_located((
                By.TAG_NAME,
                tag_tables_pje,
            )),
        )

        nome_parte = bot_data["PARTE_PETICIONANTE"]
        sleep(0.5)
        # Itera sobre os grids de partes e busca a parte peticionante para seleção
        for parte_grid in partes_grid:
            # Busca todas as linhas (tr) diretamente em todas as tabelas do grid
            linhas = [
                tr
                for table in parte_grid.find_elements(
                    By.TAG_NAME,
                    "table",
                )
                for tr in table.find_element(
                    By.TAG_NAME,
                    "tbody",
                ).find_elements(
                    By.TAG_NAME,
                    "tr",
                )
            ]

            parte = list(
                filter(
                    lambda x: x.find_elements(
                        By.TAG_NAME,
                        "td",
                    )[1].text
                    == nome_parte,
                    linhas,
                ),
            )

            if len(parte) > 0:
                parte = parte[-1]
                btn_seleciona = parte.find_elements(By.TAG_NAME, "td")[
                    0
                ].find_element(By.TAG_NAME, "mat-checkbox")
                btn_seleciona.click()
                break

        xpath_btn_prosseguir = (
            '//*[@id="area-cadastro"]/mat-action-row/div[2]/button'
        )
        sleep(1.5)

        btn_prosseguir = wait.until(
            ec.presence_of_element_located(
                (By.XPATH, xpath_btn_prosseguir),
            ),
        )
        btn_prosseguir.click()
        sleep(2.5)
        btn_prosseguir2 = wait.until(
            ec.presence_of_element_located(
                (By.XPATH, xpath_btn_prosseguir),
            ),
        )
        btn_prosseguir2.click()
        sleep(0.5)

    def vincular_outros_advogados(self) -> None:
        """Vincula outro advogado ao processo.

        >>> wait = WebDriverWait(driver, 10)

        >>> btn_adicionar_advogado = wait.until(
        >>>     ec.presence_of_element_located((
        >>>         By.XPATH,
        >>>         el.XPATH_BTN_ADICIONAR_ADVOGADO,
        >>>     )),
        >>> )

        >>> btn_adicionar_advogado.click()
        """

    def __peticao_principal(self) -> None:
        sleep(0.5)
        bot_data = self.bot_data
        wait = WebDriverWait(driver=self.driver, timeout=10)

        xpath_input_doc_principal = '//*[@id="upload-anexo-0"]'

        input_doc_principal = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                xpath_input_doc_principal,
            )),
        )
        sleep(1.5)
        nome_arquivo = formata_string(bot_data["PETICAO_PRINCIPAL"])
        path_input_doc = str(
            self.output_dir_path.joinpath(nome_arquivo),
        )

        input_doc_principal.send_keys(path_input_doc)
        sleep(10)

        salvar_arquivo = wait.until(
            ec.presence_of_element_located(
                (By.XPATH, el.XPATH_SALVA_ARQUIVO),
            ),
        )
        salvar_arquivo.click()

    def __anexos_peticao(self) -> None:
        sleep(0.5)
        bot_data = self.bot_data
        wait = WebDriverWait(driver=self.driver, timeout=10)

        btn_anexos = wait.until(
            ec.presence_of_element_located(
                (By.XPATH, el.XPATH_SALVA_ARQUIVO),
            ),
        )

        btn_anexos.click()
        sleep(0.5)
        campo_anexos = wait.until(
            ec.presence_of_element_located(
                ec.presence_of_element_located(
                    By.XPATH,
                    el.XPATH_INPUT_ANEXOS,
                ),
            ),
        )
        sleep(0.5)
        anexos_data = bot_data["ANEXOS"]
        tipo_anexos_data = bot_data["TIPO_ANEXOS"]
        anexos = anexos_data.split(",") if "," in anexos_data else [anexos_data]
        sleep(0.5)
        tipo_anexos = (
            tipo_anexos_data.split(",")
            if "," in tipo_anexos_data
            else [tipo_anexos_data]
        )

        for anexo in anexos:
            nome_arquivo = formata_string(anexo)
            path_input_doc = str(
                self.output_dir_path.joinpath(nome_arquivo),
            )
            campo_anexos.send_keys(path_input_doc)
            sleep(5.0)

        list_anexos = wait.until(
            ec.presence_of_element_located(
                (By.XPATH, el.OL_LIST_ANEXOS),
            ),
        ).find_elements(By.TAG_NAME, "li")

        sleep(0.5)
        for pos, tipo_anexo in enumerate(tipo_anexos):
            anexo = list_anexos[pos]
            elemento = el.XPATH_INPUT_TIPO_ANEXO
            input_tipo_anexo = anexo.find_element(By.XPATH, elemento)
            input_tipo_anexo.send_keys(tipo_anexo)
            sleep(0.5)

    def __assinar_salvar_comprovante(self) -> None:
        sleep(0.5)
        bot_data = self.bot_data
        wait = WebDriverWait(driver=self.driver, timeout=30)

        btn_assinar = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_BTN_ASSINAR,
            )),
        )
        btn_assinar.click()

        dialog_comprovante = wait.until(
            ec.presence_of_element_located(
                (
                    By.XPATH,
                    el.XPATH_DIALOG_COMPROVANTE,
                ),
            ),
        )
        sleep(0.5)
        processo = bot_data["NUMERO_PROCESSO"]
        pid = self.pid
        nome_comprovante = f"Comprovante Protocolo - {processo} - {pid}.png"
        path_comprovante = self.output_dir_path.joinpath(
            nome_comprovante,
        )
        with path_comprovante.open("wb") as fp:
            fp.write(dialog_comprovante.screenshot_as_png)
