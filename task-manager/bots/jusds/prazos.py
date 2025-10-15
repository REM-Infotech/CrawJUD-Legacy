"""empty."""

from __future__ import annotations

from datetime import datetime
from time import sleep
from zoneinfo import ZoneInfo

from app.common.exceptions.bot import ExecutionError
from app.decorators import shared_task
from app.decorators.bot import wrap_cls
from controllers.jusds import JusdsBot
from resources.elements import jusds as el
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


@shared_task(name="jusds.prazos", bind=True, context=ContextTask)
@wrap_cls
class Prazos(JusdsBot):
    """empty."""

    def execution(self) -> None:
        frame = self.frame
        self.total_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value

        self.finalize_execution()

    def queue(self) -> None:
        try:
            busca = self.search()

            if not busca:
                message = "Processo não encontrado"
                self.append_error(exc=message)
                return

            self.acesso_compromissos()
            self.criar_compromisso()

            confirmacao = self.confirma_salvamento()

            if not confirmacao:
                message = "Não foi possível criar compromisso!"
                self.append_error(exc=message)
                return

            message = "Compromisso / Prazo criado com sucesso!"
            self.print_comprovante(message=message)

        except (ExecutionError, Exception) as e:
            self.append_error(e)

    def acesso_compromissos(self) -> None:
        wait = WebDriverWait(self.driver, 10)
        btn_tab_compromissos = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.CSS_BTN_TAB_COMPROMISSOS,
            )),
        )

        btn_tab_compromissos.click()

    def criar_compromisso(self) -> None:
        bot_data = self.bot_data
        wait = WebDriverWait(self.driver, 10)
        btn_novo_compromisso = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_BTN_NOVO_COMPROMISSO,
            )),
        )

        btn_novo_compromisso.click()

        table_prazos = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_TABELA_COMPROMISSOS,
            )),
        )

        self.tr_prazos = table_prazos.find_elements(By.TAG_NAME, "tr")
        novo_compromisso = self.tr_prazos[-1]

        campos = novo_compromisso.find_elements(By.TAG_NAME, "td")[5:]

        campos_prazo = {
            "tipo": campos[0].find_element(By.TAG_NAME, "input"),
            "subtipo": campos[1].find_element(By.TAG_NAME, "input"),
            "descricao": campos[2].find_element(By.TAG_NAME, "input"),
            "atribuir_para": campos[3].find_element(By.TAG_NAME, "input"),
            "situacao_execucao": campos[6].find_element(By.TAG_NAME, "input"),
            "data_inicio": campos[7].find_element(By.TAG_NAME, "input"),
            "data_fim": campos[9].find_element(By.TAG_NAME, "input"),
            "valor_multa": campos[12].find_element(By.TAG_NAME, "input"),
            "valor_pgto": campos[13].find_element(By.TAG_NAME, "input"),
            "data_atualizacao": campos[14].find_element(By.TAG_NAME, "input"),
        }

        current_time = datetime.now(ZoneInfo("America/Manaus"))

        for campo_nome, elemento in list(campos_prazo.items()):
            data: str = bot_data.get(campo_nome.upper(), "")

            if campo_nome == "data_inicio" and not data:
                data = current_time.strftime("%d/%m/%Y")

            if data:
                if "valor" not in campo_nome or "data" not in campo_nome:
                    data = data.upper()

                elemento.send_keys(data)
                sleep(0.5)

        btn_salva_compromisso = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_SALVA_COMPROMISSO,
            )),
        )

        btn_salva_compromisso.click()

    def confirma_salvamento(self) -> bool:
        wait = WebDriverWait(self.driver, 10)
        table_prazos = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.XPATH_TABELA_COMPROMISSOS,
            )),
        )

        tr_prazos = table_prazos.find_elements(By.TAG_NAME, "tr")

        return len(tr_prazos) == len(self.tr_prazos)
