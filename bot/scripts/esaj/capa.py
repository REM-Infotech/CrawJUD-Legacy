import time
from contextlib import suppress
from time import sleep

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from bot.common.exceptions import ErroDeExecucao
from bot.meta.CrawJUD import CrawJUD


class capa(CrawJUD):

    def __init__(self, **kwrgs) -> None:
        super().__init__(**kwrgs)
        super().auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:

        frame = self.dataFrame()
        self.max_rows = len(frame)

        for pos, value in enumerate(frame):

            self.row = pos + 1
            self.bot_data = value
            if self.isStoped:
                break

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    super().auth_bot()

            try:
                self.queue()

            except Exception as e:

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
            self.SearchBot()
            self.append_success(self.get_process_informations())

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def get_process_informations(self) -> list:

        self.message = f"Extraindo informações do processo nº{self.bot_data.get('NUMERO_PROCESSO')}"
        self.type_log = "log"
        self.prt()

        grau = int(str(self.bot_data.get("GRAU", "1")).replace("º", ""))
        if grau == 1:

            acao: WebElement = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.elements.acao))
            ).text
            area_do_direito = "Diversos"

            if acao == "Procedimento do Juizado Especial Cível":
                area_do_direito = str(acao).replace("Procedimento do ", "")

            subarea_direito = "Geral"
            estado = "Amazonas"
            comarca = self.driver.find_element(By.ID, "foroProcesso").text

            if "Fórum de " in comarca:
                comarca = str(comarca).replace("Fórum de ", "")

            vara: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.vara_processual)
                )
            ).text.split(" ")[0]
            foro: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.elements.vara_processual)
                )
            ).text.replace(f"{vara} ", "")

            table_partes = self.driver.find_element(By.ID, self.elements.area_selecao)
            polo_ativo = (
                table_partes.find_elements(By.TAG_NAME, "tr")[0]
                .find_elements(By.TAG_NAME, "td")[1]
                .text.split("\n")[0]
            )

            tipo_parte = "Autor"
            cpf_polo_ativo = "Não consta"

            polo_passivo = (
                table_partes.find_elements(By.TAG_NAME, "tr")[1]
                .find_elements(By.TAG_NAME, "td")[1]
                .text.split("\n")[0]
            )

            tipo_passivo = "réu"
            cpf_polo_passivo = "Não consta"

            try:
                adv_polo_ativo = (
                    table_partes.find_elements(By.TAG_NAME, "tr")[0]
                    .find_elements(By.TAG_NAME, "td")[1]
                    .text.split(":")[1]
                    .replace("Advogado:", "")
                    .replace("Advogada:", "")
                    .replace("  ", "")
                )

            except Exception:
                adv_polo_ativo = "Não consta"
            escritorio_externo = "Fonseca Melo e Viana Advogados Associados"
            fase = "inicial"
            valor = ""
            with suppress(TimeoutException):
                valor: WebElement = (
                    WebDriverWait(self.driver, 1, 0.01)
                    .until(
                        EC.presence_of_element_located((By.ID, self.elements.id_valor))
                    )
                    .text
                )

            def converte_valor_causa(valor_causa) -> str:
                if "R$" in valor_causa:
                    valor_causa = float(
                        valor_causa.replace("$", "")
                        .replace("R", "")
                        .replace(" ", "")
                        .replace(".", "")
                        .replace(",", ".")
                    )
                    return "{:.2f}".format(valor_causa).replace(".", ",")

                if "R$" not in valor_causa:
                    valor_causa = float(
                        valor_causa.replace("$", "")
                        .replace("R", "")
                        .replace(" ", "")
                        .replace(",", "")
                    )
                    return "{:.2f}".format(valor_causa).replace(".", ",")

            valorDaCausa = valor
            if valor != "":
                valorDaCausa = converte_valor_causa(valor)

            sleep(0.5)
            distnotformated: WebElement = (
                self.wait.until(
                    EC.presence_of_element_located(
                        (By.ID, self.elements.data_processual)
                    )
                )
                .text.replace(" às ", "|")
                .replace(" - ", "|")
            )
            distdata = distnotformated.split("|")[0]
            processo_data = [
                self.bot_data.get("NUMERO_PROCESSO"),
                area_do_direito,
                subarea_direito,
                estado,
                comarca,
                foro,
                vara,
                distdata,
                polo_ativo,
                tipo_parte,
                cpf_polo_ativo,
                polo_passivo,
                tipo_passivo,
                cpf_polo_passivo,
                "",
                "",
                "",
                acao,
                "",
                "",
                "",
                "",
                adv_polo_ativo,
                "",
                escritorio_externo,
                valorDaCausa,
                fase,
            ]

        elif grau == 2:

            # classe: WebElement = self.wait.until(EC.presence_of_element_located(((By.XPATH, self.elements.classe_processual)))).text
            seção: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    ((By.XPATH, self.elements.selecao_processual))
                )
            ).text
            julgador: WebElement = self.wait.until(
                EC.presence_of_element_located(
                    ((By.XPATH, self.elements.orgao_processual))
                )
            ).text

            try:
                situaçãoproc = self.driver.find_element(
                    By.CSS_SELECTOR, self.elements.status_processual
                ).text
            except Exception:
                situaçãoproc = "Não Consta"

            relator: WebElement = self.wait.until(
                EC.presence_of_element_located(((By.XPATH, self.elements.relator)))
            ).text
            table_partes = self.driver.find_element(By.ID, self.elements.area_selecao)
            polo_ativo = (
                table_partes.find_elements(By.TAG_NAME, "tr")[0]
                .find_elements(By.TAG_NAME, "td")[1]
                .text.split("\n")[0]
            )
            cpf_polo_ativo = "Não consta"
            try:
                adv_polo_ativo = (
                    table_partes.find_elements(By.TAG_NAME, "tr")[0]
                    .find_elements(By.TAG_NAME, "td")[1]
                    .text.split(":")[1]
                    .replace("Advogada", "")
                    .replace("Advogado", "")
                )

            except Exception:
                adv_polo_ativo = "Não consta"
            polo_passivo = (
                table_partes.find_elements(By.TAG_NAME, "tr")[1]
                .find_elements(By.TAG_NAME, "td")[1]
                .text.split("\n")[0]
            )
            cpf_polo_passivo = "Não consta"

            try:
                adv_polo_passivo = (
                    table_partes.find_elements(By.TAG_NAME, "tr")[1]
                    .find_elements(By.TAG_NAME, "td")[1]
                    .text.split(":")[1]
                    .replace("Advogada", "")
                    .replace("Advogado", "")
                )

            except Exception:
                adv_polo_passivo = "Não consta"
            processo_data = [
                self.bot_data.get("NUMERO_PROCESSO"),
                situaçãoproc,
                seção,
                julgador,
                relator,
                polo_ativo,
                adv_polo_ativo,
                polo_passivo,
                adv_polo_passivo,
            ]
            try:
                self.append_success(processo_data)
            except Exception:
                pass

        return processo_data
