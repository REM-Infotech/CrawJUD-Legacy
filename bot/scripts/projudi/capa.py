import re
import time
from contextlib import suppress
from datetime import datetime

from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.common.by import By
from urllib3.exceptions import MaxRetryError

from bot.common.exceptions import ErroDeExecucao
from bot.meta.CrawJUD import CrawJUD


class capa(CrawJUD):

    def __init__(self, **kwrgs) -> None:
        super().__init__(**kwrgs)
        super().setup()
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

                old_message = None
                check_window = any(
                    [isinstance(e, NoSuchWindowException), isinstance(e, MaxRetryError)]
                )
                if check_window:

                    with suppress(Exception):
                        super().DriverLaunch(
                            message="Webdriver encerrado inesperadamente, reinicializando..."
                        )

                        old_message = self.message

                        super().auth_bot()

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

        search = self.SearchBot()

        if search is not True:
            raise ErroDeExecucao("Processo não encontrado!")

        self.driver.refresh()
        data = self.get_process_informations()
        self.append_success(data, "Informações do processo extraidas com sucesso!")

    def get_process_informations(self) -> list:

        self.message = (
            f"Obtendo informações do processo {self.bot_data.get('NUMERO_PROCESSO')}..."
        )
        self.type_log = "log"
        self.prt()

        btn_partes = self.driver.find_element(By.CSS_SELECTOR, self.elements.btn_partes)
        btn_partes.click()

        try:
            includeContent = self.driver.find_element(
                By.ID, self.elements.includeContent_capa
            )
        except Exception:
            time.sleep(3)
            self.driver.refresh()
            time.sleep(1)
            includeContent = self.driver.find_element(
                By.ID, self.elements.includeContent_capa
            )

        tablePoloAtivo = includeContent.find_elements(
            By.CLASS_NAME, self.elements.resulttable
        )[0]
        nomePoloAtivo = (
            tablePoloAtivo.find_element(By.XPATH, ".//tbody")
            .find_elements(By.XPATH, ".//tr")[0]
            .find_elements(By.XPATH, ".//td")[1]
            .text.replace("(citação online)", "")
        )

        if " representado" in nomePoloAtivo:
            nomePoloAtivo = str(nomePoloAtivo.split(" representado")[0])

        cpfPoloAtivo = (
            tablePoloAtivo.find_element(By.XPATH, ".//tbody")
            .find_elements(By.XPATH, ".//tr")[0]
            .find_elements(By.XPATH, ".//td")[3]
            .text
        )
        advPoloAtivo = (
            tablePoloAtivo.find_element(By.XPATH, ".//tbody")
            .find_elements(By.XPATH, ".//tr")[0]
            .find_elements(By.XPATH, ".//td")[5]
            .text
        )

        tablePoloPassivo = includeContent.find_elements(
            By.CLASS_NAME, self.elements.resulttable
        )[1]
        nomePoloPassivo = (
            tablePoloPassivo.find_element(By.XPATH, ".//tbody")
            .find_elements(By.XPATH, ".//tr")[0]
            .find_elements(By.XPATH, ".//td")[1]
            .text.replace("(citação online)", "")
        )
        cpfPoloPassivo = (
            tablePoloPassivo.find_element(By.XPATH, ".//tbody")
            .find_elements(By.XPATH, ".//tr")[0]
            .find_elements(By.XPATH, ".//td")[3]
            .text
        )

        btn_infogeral = self.driver.find_element(
            By.CSS_SELECTOR, self.elements.btn_infogeral
        )
        btn_infogeral.click()

        try:
            includeContent = self.driver.find_element(
                By.ID, self.elements.includeContent_capa
            )
        except Exception:
            time.sleep(3)
            self.driver.refresh()
            time.sleep(1)
            includeContent = self.driver.find_element(
                By.ID, self.elements.includeContent_capa
            )

        includeContent = includeContent.find_element(By.CLASS_NAME, "form")

        area_direito = str(
            includeContent.find_elements(By.XPATH, ".//tr")[0]
            .find_elements(By.XPATH, ".//td")[4]
            .text
        )

        if area_direito.lower() == "juizado especial cível":

            area_direito = (
                area_direito.lower()
                .replace("juizado especial cível", "juizado especial")
                .capitalize()
            )

        foro = str(
            includeContent.find_elements(By.XPATH, ".//tr")[1]
            .find_elements(By.XPATH, ".//td")[4]
            .text
        )

        comarca = foro

        if "je cível" in foro.lower():

            foro = foro.lower().replace("je cível", "cível").capitalize()

        if " da comarca de " in foro:
            comarca = foro.split(" da comarca de ")[1]

        if "cível" in comarca.lower():

            comarca = comarca.split(" - ")[0].capitalize()

        data_distribuicao = (
            includeContent.find_elements(By.XPATH, ".//tr")[2]
            .find_elements(By.XPATH, ".//td")[1]
            .text
        )

        if " às " in data_distribuicao:
            data_distribuicao = data_distribuicao.split(" às ")[0]
            data_distribuicao = datetime.strptime(data_distribuicao, "%d/%m/%Y")

        infoproc = self.driver.find_element(By.CSS_SELECTOR, self.elements.infoproc)
        tablestatusproc = infoproc.find_element(By.TAG_NAME, "tbody").find_elements(
            By.TAG_NAME, "tr"
        )[0]

        try:
            statusproc = tablestatusproc.find_elements(By.TAG_NAME, "td")[1].text
        except Exception:
            statusproc = "Não Consta"

        # try:
        #     juizproc = (
        #         includeContent.find_elements(By.XPATH, ".//tr")[2]
        #         .find_elements(By.XPATH, ".//td")[4]
        #         .text
        #     )
        # except Exception:
        #     juizproc = "Não Consta"

        try:
            includeContent = self.driver.find_element(
                By.ID, self.elements.includeContent_capa
            )
        except Exception:
            time.sleep(3)
            self.driver.refresh()
            time.sleep(1)
            includeContent = self.driver.find_element(
                By.ID, self.elements.includeContent_capa
            )

        includeContent = includeContent.find_element(
            By.CLASS_NAME, "form"
        ).find_elements(By.TAG_NAME, "tr")

        for it in includeContent:

            get_label = it.find_elements(By.TAG_NAME, "td")[0].text

            if get_label == "Valor da Causa:":

                valorDaCausa = str(it.find_elements(By.TAG_NAME, "td")[1].text)
                break

        # assunto_proc = self.driver.find_element(
        #     By.CSS_SELECTOR, self.elements.assunto_proc
        # ).text.split(" - ")[1]

        if "¤" in valorDaCausa:
            valorDaCausa = valorDaCausa.replace("¤", "")

        pattern = r"(?<!\S)(?:US\$[\s]?|R\$[\s]?|[\$]?)\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?(?!\S)"
        matches = re.findall(pattern, valorDaCausa)
        if len(matches) > 0:

            def convert_to_float(value):
                # Remover símbolos de moeda e espaços
                value = re.sub(r"[^\d.,]", "", value)

                # Identificar se o formato é BRL (com vírgula para decimais) ou USD (com ponto para decimais)
                if "," in value and "." in value:
                    # Assumir formato USD se houver tanto ',' quanto '.'
                    parts = value.split(".")
                    if len(parts[-1]) == 2:
                        value = value.replace(",", "")
                    elif not len(parts[-1]) == 2:
                        value = value.replace(".", "").replace(",", ".")
                elif "," in value:
                    # Assumir formato BRL
                    value = value.replace(".", "").replace(",", ".")
                elif "." in value:
                    # Assumir formato USD
                    value = value.replace(",", "")

                return float(value)

            valorDaCausa = convert_to_float(matches[0])

        vara = foro.split(" ")[0]
        if "vara única" in foro.lower():
            vara = foro.split(" da ")[0]

        if " - " in advPoloAtivo:

            # get_oab = advPoloAtivo.split(" - ")[0]
            advPoloAtivo = advPoloAtivo.split(" - ")[1]

        # elif advPoloAtivo == "Parte sem advogado":
        #     get_oab = ""

        processo_data = [
            self.bot_data.get("NUMERO_PROCESSO"),
            area_direito,
            "Geral",
            "Amazonas",
            comarca,
            foro,
            vara,
            data_distribuicao,
            nomePoloAtivo,
            "Autor",
            cpfPoloAtivo,
            nomePoloPassivo,
            "réu",
            cpfPoloPassivo,
            statusproc,
            "Liliane Da Silva Roque",
            advPoloAtivo,
            "Fonseca Melo e Viana Advogados Associados",
            valorDaCausa,
        ]

        return processo_data
