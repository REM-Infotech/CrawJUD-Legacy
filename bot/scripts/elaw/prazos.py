import os
import time
from contextlib import suppress

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from bot.common.exceptions import ErroDeExecucao

from ...CrawJUD import CrawJUD
from ...meta import PropertiesCrawJUD


class prazos(PropertiesCrawJUD):

    def __init__(self, **kwrgs) -> None:
        super().__init__(**kwrgs)
        CrawJUD.setup()
        CrawJUD.auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:

        frame = CrawJUD.dataFrame()
        self.max_rows = len(frame)

        for pos, value in enumerate(frame):

            self.row = pos + 1
            self.bot_data = value
            if self.isStoped:
                break

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    CrawJUD.auth_bot()

            try:
                self.queue()

            except Exception as e:

                old_message = None
                windows = self.driver.window_handles

                if len(windows) == 0:
                    with suppress(Exception):
                        super().DriverLaunch(
                            message="Webdriver encerrado inesperadamente, reinicializando..."
                        )

                    old_message = self.message

                    CrawJUD.auth_bot()

                if old_message is None:
                    old_message = self.message
                message_error = str(e)

                self.type_log = "error"
                self.message_error = f"{message_error}. | Operação: {old_message}"
                self.prt()

                self.bot_data.update({"MOTIVO_ERRO": self.message_error})
                self.append_error(self.bot_data)

                self.message_error = None

        self.finalize_execution()

    def queue(self) -> None:

        try:
            search = self.SearchBot()
            if not search:
                self.message = "Buscando Processo"
                raise ErroDeExecucao("Não Encontrado!")

            comprovante = ""
            self.data_Concat = (
                f'{self.bot_data["DATA_AUDIENCIA"]} {self.bot_data["HORA_AUDIENCIA"]}'
            )
            self.message = "Processo Encontrado!"
            self.type_log = "log"
            self.prt()

            self.TablePautas()
            chk_lancamento = self.CheckLancamento()

            if chk_lancamento:
                self.message = "Já existe lançamento para esta pauta"
                self.type_log = "info"
                chk_lancamento.update(
                    {"MENSAGEM_COMCLUSAO": "REGISTROS ANTERIORES EXISTENTES!"}
                )

                comprovante = chk_lancamento

            if not comprovante:
                self.NovaPauta()
                self.save_Prazo()
                comprovante = self.CheckLancamento()
                if not comprovante:
                    raise ErroDeExecucao(
                        "Não foi possível comprovar lançamento, verificar manualmente"
                    )

                self.message = "Pauta lançada!"

            self.append_success([comprovante], self.message)

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def TablePautas(self) -> None:

        try:

            switch_pautaAndamento = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.switch_pautaAndamento
            )

            switch_pautaAndamento.click()

            self.message = (
                f"Verificando se existem pautas para o dia {self.data_Concat}"
            )
            self.type_log = "log"
            self.prt()

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def NovaPauta(self) -> None:

        try:
            self.message = "Lançando nova audiência"
            self.type_log = "log"
            self.prt()

            btn_NovaAudiencia = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.btn_NovaAudiencia)
                )
            )

            btn_NovaAudiencia.click()

            # Info tipo Audiencia
            self.message = "Informando tipo de audiência"
            self.type_log = "log"
            self.prt()

            selectorTipoAudiencia: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.selectorTipoAudiencia)
                )
            )

            items = selectorTipoAudiencia.find_elements(By.TAG_NAME, "option")
            opt_itens: dict[str, str] = {}
            for item in items:

                value_item = item.get_attribute("value")
                text_item = self.driver.execute_script(
                    f"return $(\"option[value='{value_item}']\").text();"
                )

                opt_itens.update({text_item.upper(): value_item})

            value_opt = opt_itens.get(self.bot_data["TIPO_AUDIENCIA"].upper())
            if value_opt:
                command = (
                    f"$('{self.elements.selectorTipoAudiencia}').val(['{value_opt}']);"
                )
                self.driver.execute_script(command)

                command2 = (
                    f"$('{self.elements.selectorTipoAudiencia}').trigger('change');"
                )
                self.driver.execute_script(command2)

            # Info Data Audiencia
            self.message = "Informando data da Audiência"
            self.type_log = "log"
            self.prt()

            DataAudiencia: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.DataAudiencia)
                )
            )

            DataAudiencia.send_keys(self.data_Concat)

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def save_Prazo(self) -> None:

        try:

            self.message = "Salvando..."
            self.type_log = "log"
            self.prt()

            btn_Salvar = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.btn_Salvar
            )

            btn_Salvar.click()

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def CheckLancamento(self) -> dict[str, str] | None:

        try:

            tablePrazos: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.tablePrazos)
                )
            )

            tablePrazos: list[WebElement] = tablePrazos.find_elements(By.TAG_NAME, "tr")

            data = None
            for item in tablePrazos:

                if item.text == "Nenhum registro encontrado!":
                    return None

                data_Prazo = str(item.find_elements(By.TAG_NAME, "td")[4].text)

                tipo = str(item.find_elements(By.TAG_NAME, "td")[5].text)

                chk_tipo = tipo.upper() == "AUDIÊNCIA"
                chk_dataAudiencia = data_Prazo == self.data_Concat

                if chk_tipo and chk_dataAudiencia:

                    nProc_pid = f'{self.bot_data["NUMERO_PROCESSO"]} - {self.pid}'

                    nameComprovante = f"Comprovante - {nProc_pid}.png"
                    idPrazo = str(item.find_elements(By.TAG_NAME, "td")[2].text)

                    item.screenshot(os.path.join(self.output_dir_path, nameComprovante))

                    data = {
                        "NUMERO_PROCESSO": str(self.bot_data["NUMERO_PROCESSO"]),
                        "MENSAGEM_COMCLUSAO": "PRAZO LANÇADO",
                        "ID_PRAZO": idPrazo,
                        "NOME_COMPROVANTE": nameComprovante,
                    }

            return data

        except Exception as e:
            raise ErroDeExecucao(e=e)
