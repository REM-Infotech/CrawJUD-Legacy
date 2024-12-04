import time
from contextlib import suppress
from datetime import datetime

import pytz
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from urllib3.exceptions import MaxRetryError

from bot.meta.CrawJUD import CrawJUD


class busca_pags(CrawJUD):

    def __init__(self, **kwrgs) -> None:
        super().__init__(**kwrgs)
        super().auth_bot()
        self.datetimeNOW = datetime.now(pytz.timezone("America/Manaus")).strftime(
            "%d-%m-%Y"
        )
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

        self.get_page_custas_pagas()
        self.page_custas()

    def get_page_custas_pagas(self) -> None:

        generatepdf: WebElement = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, self.elements.get_page_custas_pagas)
            )
        )
        onclick_value = generatepdf.get_attribute("onclick")
        url_start = onclick_value.find("'") + 1
        url_end = onclick_value.find("'", url_start)
        url = onclick_value[url_start:url_end]
        self.driver.get(url)

    def page_custas(self) -> None:

        divcustaspagas: list[WebElement] = self.wait.until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "div"))
        )
        total = 0
        for divcorreta in divcustaspagas:

            nomediv = None

            with suppress(Exception):
                nomediv = divcorreta.find_element(
                    By.CLASS_NAME, "tituloGridCustas"
                ).text

            if nomediv is None:
                continue

            if "Lista de custas pagas" in nomediv:

                self.message = "Extraindo dados..."
                self.type_log = "log"
                self.prt()

                find_table_pgmt = divcorreta.find_element(
                    By.CSS_SELECTOR, 'table[class="spwTabelaGrid"]'
                )

                tr_rows = find_table_pgmt.find_elements(By.TAG_NAME, "tr")
                self.roleta = 0

                for rows in tr_rows:

                    try:
                        checkifclass = rows.get_attribute("class")
                        if checkifclass == "":
                            tipo_custa = rows.find_elements(By.TAG_NAME, "td")[0].text
                            emissor = rows.find_elements(By.TAG_NAME, "td")[1].text
                            data_calculo = str(
                                rows.find_elements(By.TAG_NAME, "td")[2].text
                            )

                            data_calculo = datetime.strptime(data_calculo, "%d/%m/%Y")

                            valor_custa = (
                                str(rows.find_elements(By.TAG_NAME, "td")[3].text)
                                .replace(".", "")
                                .replace(",", ".")
                            )

                            valor_custa = float(valor_custa)

                            cód_guia = str(
                                rows.find_elements(By.TAG_NAME, "td")[4].text
                            )
                            parcelaguia = rows.find_elements(By.TAG_NAME, "td")[5].text

                            data_pagamento = str(
                                rows.find_elements(By.TAG_NAME, "td")[6].text
                            )

                            data_pagamento = datetime.strptime(
                                data_pagamento, "%d/%m/%Y"
                            )

                            total += valor_custa

                            self.roleta = self.roleta + 1
                            data = [
                                self.bot_data.get("NUMERO_PROCESSO"),
                                tipo_custa,
                                emissor,
                                data_calculo,
                                valor_custa,
                                cód_guia,
                                parcelaguia,
                                data_pagamento,
                            ]
                            self.append_success()
                        elif not checkifclass == "":
                            continue

                    except Exception:
                        tipo_custa = rows.find_elements(By.TAG_NAME, "td")[0].text
                        emissor = rows.find_elements(By.TAG_NAME, "td")[1].text
                        data_calculo = str(
                            rows.find_elements(By.TAG_NAME, "td")[2].text
                        )

                        data_calculo = datetime.strptime(data_calculo, "%d/%m/%Y")

                        valor_custa = str(rows.find_elements(By.TAG_NAME, "td")[3].text)

                        valor_custa = float(valor_custa)

                        cód_guia = str(rows.find_elemens(By.TAG_NAME, "td")[4].text)
                        parcelaguia = rows.find_elements(By.TAG_NAME, "td")[5].text
                        data_pagamento = datetime.strptime(
                            str(rows.find_elements(By.TAG_NAME, "td")[6].text)
                        )

                        data_pagamento = datetime.strptime(data_pagamento, "%d/%m/%Y")
                        self.roleta = self.roleta + 1
                        total += valor_custa

                        data = [
                            self.bot_data.get("NUMERO_PROCESSO"),
                            tipo_custa,
                            emissor,
                            data_calculo,
                            valor_custa,
                            cód_guia,
                            parcelaguia,
                            data_pagamento,
                        ]
                        self.append_success(data)

            elif "Lista de custas pagas" not in nomediv:
                continue

            fileN = f"Total - {self.pid} - {self.datetimeNOW}.xlsx"
            self.append_success(
                [self.bot_data.get("NUMERO_PROCESSO"), total], fileN=fileN
            )
