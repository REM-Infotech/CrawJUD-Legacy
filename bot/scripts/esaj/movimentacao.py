import time
from datetime import datetime
from time import sleep

# Selenium Imports
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from bot.common.exceptions import ErroDeExecucao
from bot.meta.CrawJUD import CrawJUD


class movimentacao(CrawJUD):

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
            self.appends = []
            self.resultados = []
            search = bool(self.SearchBot())

            if search is True:
                self.get_moves()
                self.append_moves()

            elif search is False:
                raise ErroDeExecucao("Processo não encontrado!")

        except Exception as e:
            raise ErroDeExecucao(e=e)

    def get_moves(self) -> None:

        show_all: WebElement = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'a[id="linkmovimentacoes"]')
            )
        )

        self.interact.scroll_to(show_all)

        # Rolar até o elemento
        self.driver.execute_script("arguments[0].scrollIntoView(true);", show_all)

        # Use JavaScript para clicar no elemento
        self.driver.execute_script("arguments[0].click();", show_all)

        sleep(0.5)

        try:

            table_moves = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.movimentacoes
            )
            self.driver.execute_script(
                'document.querySelector("#tabelaTodasMovimentacoes").style.display = "block"'
            )

        except Exception:
            table_moves = self.driver.find_element(
                By.ID, self.elements.ultimas_movimentacoes
            )
            self.driver.execute_script(
                'document.querySelector("#tabelaUltimasMovimentacoes").style.display = "block"'
            )

        itens = table_moves.find_elements(By.TAG_NAME, "tr")

        palavra_chave = str(self.bot_data.get("PALAVRA_CHAVE"))
        termos = [palavra_chave]

        if "," in palavra_chave:
            termos = palavra_chave.replace(", ", ",").split(",")

        for termo in termos:

            self.message = f'Buscando movimentações que contenham "{termo}"'
            self.type_log = "log"

            for item in itens:
                td_tr = item.find_elements(By.TAG_NAME, "td")
                mov = td_tr[2].text

                if termo.lower() in mov.lower():
                    data_mov = td_tr[0].text

                    try:
                        if type(data_mov) is str:
                            data_mov = datetime.strptime(
                                data_mov.replace("/", "-"), "%d-%m-%Y"
                            )

                    except Exception:
                        pass

                    name_mov = mov.split("\n")[0]
                    text_mov = td_tr[2].find_element(By.TAG_NAME, "span").text
                    self.appends.append(
                        [
                            self.bot_data.get("NUMERO_PROCESSO"),
                            data_mov,
                            name_mov,
                            text_mov,
                            "",
                            "",
                        ]
                    )
