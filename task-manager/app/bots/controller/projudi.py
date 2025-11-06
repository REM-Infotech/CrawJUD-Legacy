"""Módulo para a classe de controle dos robôs PROJUDI."""

from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

from app.bots.head import CrawJUD
from app.resources import value_check
from app.resources.auth._projudi import AutenticadorProjudi
from app.resources.formatadores import formata_string, normalizar
from app.resources.search.projudi import ProjudiSearch

if TYPE_CHECKING:
    from bs4._typing import _SomeTags


class ProjudiBot(CrawJUD):
    """Classe de controle para robôs do PROJUDI."""

    url_segunda_instancia: str = None
    rows_data: _SomeTags

    def __init__(self) -> None:
        self.search = ProjudiSearch(self)
        self.auth = AutenticadorProjudi(self)

    def parse_data(self, inner_html: str) -> dict[str, str]:
        """Extrai dados do HTML do processo.

        Args:
            inner_html (str): HTML da página do processo.

        Returns:
            dict[str, str]: Dados extraídos do processo.

        """
        soup = BeautifulSoup(inner_html, "html.parser")
        dados = {}
        # percorre todas as linhas <tr>

        self.rows_data = []
        for table_row in soup.find_all("tr"):
            table_row_data = table_row.find_all("td")
            self.rows_data.extend(table_row_data)

        for pos, td in enumerate(self.rows_data):
            lbl_tag = td.find("label")
            if lbl_tag:
                label = normalizar(lbl_tag.get_text().rstrip(":"))
                valor = self.__get_text(pos)

                if value_check(label, valor):
                    dados[formata_string(label)] = valor

        return dados

    def __get_text(self, pos: int) -> str:
        i = pos + 1
        while i < len(self.rows_data):
            valor = normalizar(
                self.rows_data[i].get_text(" ", strip=True),
            )
            if valor and valor != " ":
                return valor
            i += 1
        return None
