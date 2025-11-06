"""Automações para processos judiciais no Projudi."""

from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from app.bots.controller.projudi import ProjudiBot
from app.interfaces.projudi import (
    PartesProjudiDict,
    RepresentantesProjudiDict,
)
from app.resources.elements import projudi as el
from constants import INTIMACAO_ELETRONICA

if TYPE_CHECKING:
    from app.types import Dict


class PrimeiraInstancia(ProjudiBot):
    """Automações para processos de 1ª instância no Projudi.

    Esta classe herda de ProjudiBot e contém métodos para extrair
    informações gerais, processuais e das partes de processos judiciais
    no sistema Projudi.
    """

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

    def _partes_primeiro_grau(
        self,
        numero_processo: str,
    ) -> tuple[
        list[PartesProjudiDict],
        list[RepresentantesProjudiDict],
    ]:
        wait = self.wait

        btn_partes = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                el.btn_partes,
            )),
        )

        btn_partes.click()
        grouptable_partes = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                el.partes_projudi,
            )),
        )

        partes: list[Dict] = []
        advogados: list[Dict] = []

        for table in grouptable_partes.find_elements(
            By.TAG_NAME,
            "table",
        ):
            tbody_table = table.find_element(By.TAG_NAME, "tbody")
            inner_html = tbody_table.get_attribute("innerHTML")
            parte, advogado = self._partes_extract_primeiro_grau(
                html=inner_html,
                processo=numero_processo,
            )

            partes.extend(parte)
            advogados.extend(advogado)

        return partes, advogados

    def _partes_extract_primeiro_grau(
        self,
        html: str,
        processo: str,
    ) -> tuple[
        list[PartesProjudiDict],
        list[RepresentantesProjudiDict],
    ]:
        """Extraia informações das partes do processo na tabela do Projudi.

        Args:
            html (str): HTML da página contendo a tabela de partes.
            processo(str): Numero processo

        Returns:
            tuple: advogados e partes

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
            nome_parte = str(tds[1].get_text(strip=True))
            # Extrai documento (RG ou similar)
            documento_parte = str(tds[2].get_text(strip=True))
            # Extrai CPF
            cpf_cnpj_parte = str(tds[3].get_text(strip=True))
            # Extrai OABs e advogados
            advogados_parte = ", ".join([
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
                        endereco = str(
                            endereco_div.get_text(" ", strip=True),
                        )

            if nome_parte != "Descrição:":
                for li in tds[5].find_all("li"):
                    advogado_e_oab = " ".join(
                        str(li.get_text(" ", strip=True)).split(),
                    ).split(" - ")
                    if advogado_e_oab[1] != INTIMACAO_ELETRONICA:
                        advogados.append(
                            RepresentantesProjudiDict(
                                NUMERO_PROCESSO=processo,
                                NOME=advogado_e_oab[1],
                                OAB=advogado_e_oab[0],
                                REPRESENTADO=nome_parte,
                            ),
                        )

                partes.append(
                    PartesProjudiDict(
                        NUMERO_PROCESSO=processo,
                        NOME=nome_parte,
                        DOCUMENTO=documento_parte,
                        CPF_CNPJ=cpf_cnpj_parte,
                        ADVOGADOS=advogados_parte,
                        ENDERECO=endereco,
                    ),
                )

        return partes, advogados
