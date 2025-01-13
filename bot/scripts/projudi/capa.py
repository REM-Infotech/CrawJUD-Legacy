import re
import time
from contextlib import suppress
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

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
                windows = self.driver.window_handles

                if len(windows) == 0:
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

        try:
            search = self.SearchBot()

            if search is not True:
                raise ErroDeExecucao("Processo não encontrado!")

            self.driver.refresh()
            data = self.get_process_informations()
            self.append_success(data, "Informações do processo extraidas com sucesso!")

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def get_process_informations(self) -> list:

        try:

            grau = int(str(self.bot_data.get("GRAU", "1")).replace("º", ""))
            process_info = {}
            process_info.update(
                {"NUMERO_PROCESSO": self.bot_data.get("NUMERO_PROCESSO")}
            )

            def format_vl_causa(valorDaCausa: str) -> float | str:
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

                    return convert_to_float(matches[0])

                return valorDaCausa

            self.message = f"Obtendo informações do processo {self.bot_data.get('NUMERO_PROCESSO')}..."
            self.type_log = "log"
            self.prt()

            btn_infogeral = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.btn_infogeral
            )
            btn_infogeral.click()

            includeContent: list[WebElement] = []

            element_content = self.elements.primeira_instform1
            element_content2 = self.elements.primeira_instform2

            if grau == 2:
                element_content = self.elements.segunda_instform
                element_content2 = element_content

            includeContent.append(
                self.driver.find_element(By.CSS_SELECTOR, element_content)
            )
            includeContent.append(
                self.driver.find_element(By.CSS_SELECTOR, element_content2)
            )

            for incl in includeContent:
                itens = list(
                    filter(
                        lambda x: len(x.find_elements(By.TAG_NAME, "td")) > 1,
                        incl.find_element(By.TAG_NAME, "tbody").find_elements(
                            By.TAG_NAME, "tr"
                        ),
                    )
                )

                for item in itens:

                    labels = list(
                        filter(
                            lambda x: x.text.strip() != "",
                            item.find_elements(
                                By.CSS_SELECTOR,
                                "td.label, td.labelRadio > label",
                            ),
                        )
                    )
                    # para teste
                    # for value in item.find_elements(By.CSS_SELECTOR, "td"):
                    #     print(value.text.strip())

                    values = list(
                        filter(
                            lambda x: x.text.strip() != ""
                            and not x.get_attribute("class"),
                            item.find_elements(By.TAG_NAME, "td"),
                        )
                    )

                    for pos, label in enumerate(labels):

                        if len(labels) != len(values):
                            continue

                        not_formated_label = label.text
                        label_text = (
                            self.format_String(label.text).upper().replace(" ", "_")
                        )

                        indice = labels.index(label)
                        value_text = values[indice].text

                        if label_text == "VALOR_DA_CAUSA":
                            value_text = format_vl_causa(value_text)

                        elif (
                            "DATA" in label_text
                            or "DISTRIBUICAO" in label_text
                            or "AUTUACAO" in label_text
                        ):

                            if " às " in value_text:
                                value_text = value_text.split(" às ")[0]

                            if self.text_is_a_date(value_text) is True:
                                value_text = datetime.strptime(value_text, "%d/%m/%Y")

                        elif not_formated_label != value_text:
                            process_info.update(
                                {label_text: " ".join(value_text.split(" ")).upper()}
                            )

            btn_partes = self.elements.btn_partes
            if grau == 2:

                btn_partes = btn_partes.replace("2", "1")

            btn_partes = self.driver.find_element(By.CSS_SELECTOR, btn_partes)
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

            result_table = includeContent.find_elements(
                By.CLASS_NAME, self.elements.resulttable
            )

            for pos, parte_info in enumerate(result_table):

                h4_name = list(
                    filter(
                        lambda x: x.text != "" and x is not None,
                        includeContent.find_elements(By.TAG_NAME, "h4"),
                    )
                )
                tipo_parte = (
                    self.format_String(h4_name[pos].text).replace(" ", "_").upper()
                )

                nome_colunas = []

                for column in parte_info.find_element(
                    By.TAG_NAME, "thead"
                ).find_elements(By.TAG_NAME, "th"):
                    nome_colunas.append(column.text.upper())

                for parte in parte_info.find_element(
                    By.TAG_NAME, "tbody"
                ).find_elements(By.XPATH, self.elements.table_moves):

                    for pos_, nome_coluna in enumerate(nome_colunas):

                        key = "_".join(
                            (
                                self.format_String(nome_coluna)
                                .replace(" ", "_")
                                .upper(),
                                tipo_parte,
                            )
                        )
                        value = parte.find_elements(By.TAG_NAME, "td")[pos_].text

                        if value:

                            " ".join(value.split(" "))

                            if "\n" in value:
                                value = " | ".join(value.split("\n"))
                                process_info.update({key: value})
                                continue

                            process_info.update({key: value})

            return [process_info]

        except Exception as e:
            e
            raise e
