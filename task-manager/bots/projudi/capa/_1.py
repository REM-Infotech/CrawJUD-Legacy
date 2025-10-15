from __future__ import annotations

from bs4 import BeautifulSoup
from controllers.projudi import ProjudiBot
from resources.elements import projudi as el
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

type ListPartes = list[tuple[list[dict[str, str]], list[dict[str, str]]]]


class PrimeiraInstancia(ProjudiBot):
    def _informacoes_gerais_primeiro_grau(self) -> None:
        wait = self.wait
        search_by = (
            By.CSS_SELECTOR,
            el.btn_infogeral,
        )
        expected = ec.presence_of_element_located(search_by)
        info_geral = wait.until(expected)
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

    def _partes_primeiro_grau(self, numero_processo: str) -> None:
        wait = self.wait

        btn_partes = wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, el.btn_partes)),
        )

        btn_partes.click()
        grouptable_partes = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.partes_projudi,
            )),
        )

        for table in grouptable_partes.find_elements(By.TAG_NAME, "table"):
            tbody_table = table.find_element(By.TAG_NAME, "tbody")
            inner_html = tbody_table.get_attribute("innerHTML")
            self._partes_extract_primeiro_grau(
                html=inner_html,
                processo=numero_processo,
            )

    def _partes_extract_primeiro_grau(self, html: str, processo: str) -> None:
        """Extraia informações das partes do processo na tabela do Projudi.

        Args:
            html (str): HTML da página contendo a tabela de partes.
            processo(str): Numero processo

        """
        soup = BeautifulSoup(html, "html.parser")
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
                        "Número do processo": processo,
                        "Nome": advogado_e_oab[1],
                        "OAB": advogado_e_oab[0],
                        "Representado": nome,
                    })

                partes.append({
                    "Número do processo": processo,
                    "Nome": nome,
                    "Documento": documento,
                    "Cpf": cpf,
                    "Advogados": advs,
                    "Endereco": endereco,
                })

        self.to_add_partes.extend(partes)
        self.to_add_representantes.extend(advogados)
