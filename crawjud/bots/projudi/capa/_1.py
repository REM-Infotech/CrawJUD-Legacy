from __future__ import annotations

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from crawjud.controllers.projudi import ProjudiBot
from crawjud.resources.elements import projudi as el

type ListPartes = list[tuple[list[dict[str, str]], list[dict[str, str]]]]


class PrimeiraInstancia(ProjudiBot):
    def _informacoes_gerais_primeiro_grau(self) -> None:
        wait = self.wait

        info_geral = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'li[id="tabItemprefix0"]',
            )),
        )

        info_geral.click()

        table_info_geral = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.info_geral_table_primeiro_grau,
            )),
        )

        inner_html = table_info_geral.get_attribute("innerHTML")
        return self.parse_data(inner_html=inner_html)

    def _info_processual_primeiro_grau(self) -> dict[str, str]:
        wait = self.wait

        table_info_processual = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.info_processual_primeiro_grau,
            )),
        )

        inner_html = table_info_processual.get_attribute("innerHTML")
        return self.parse_data(inner_html=inner_html)

    def _partes_primario_grau(
        self,
        numero_processo: str,
    ) -> list[tuple[list[dict[str, str]], list[dict[str, str]]]]:
        wait = self.wait

        btn_partes = wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, el.btn_partes)),
        )

        btn_partes.click()
        list_partes: list[
            tuple[list[dict[str, str]], list[dict[str, str]]]
        ] = []
        grouptable_partes = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.partes_projudi,
            )),
        )

        for table in grouptable_partes.find_elements(By.TAG_NAME, "table"):
            tbody_table = table.find_element(By.TAG_NAME, "tbody")
            inner_html = tbody_table.get_attribute("innerHTML")
            list_partes.append(
                self._partes_projudi(
                    inner_html=inner_html,
                    numero_processo=numero_processo,
                ),
            )

        return list_partes

    def _partes_projudi(
        self,
        inner_html: str,
        numero_processo: str,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        """Extraia informações das partes do processo na tabela do Projudi.

        Args:
            inner_html (str): HTML da página contendo a tabela de partes.
            numero_processo(str): Numero processo

        Returns:
            (tuple[list[dict[str, str]], list[dict[str, str]]]):
                Lista de dicionários com dados das partes.

        """
        soup = BeautifulSoup(inner_html, "html.parser")
        partes: list[dict[str, str]] = []
        advogados: list[dict[str, str]] = []
        endereco = ""

        # Encontra todas as linhas principais das partes
        for tr in soup.find_all("tr", class_="even"):
            tds = tr.find_all("td")
            if not tds or len(tds) < 6:
                continue
            # Extrai nome
            nome = str(tds[1].get_text(strip=True))
            # Extrai documento (RG ou similar)
            documento = str(tds[2].get_text(strip=True))
            # Extrai CPF
            cpf = str(tds[3].get_text(strip=True))
            # Extrai OABs e advogados
            advs = ", ".join([
                " ".join(str(li.get_text(" ", strip=True)).split())
                for li in tds[5].find_all("li")
            ])

            # Busca o id da linha expandida para endereço
            row_id = tr.get("id")
            if row_id:
                row_detalhe = soup.find("tr", id=f"row{row_id}")
                if row_detalhe:
                    endereco_div = row_detalhe.find(
                        "div",
                        class_="extendedinfo",
                    )
                    if endereco_div:
                        endereco = str(endereco_div.get_text(" ", strip=True))

            if nome != "Descrição:":
                for li in tds[5].find_all("li"):
                    advogado_e_oab = " ".join(
                        str(li.get_text(" ", strip=True)).split(),
                    ).split(" - ")

                    advogados.append({
                        "Número do processo": numero_processo,
                        "Nome": advogado_e_oab[1],
                        "OAB": advogado_e_oab[0],
                        "Representado": nome,
                    })

                partes.append({
                    "Número do processo": numero_processo,
                    "Nome": nome,
                    "Documento": documento,
                    "Cpf": cpf,
                    "Advogados": advs,
                    "Endereco": endereco,
                })

        return partes, advogados
