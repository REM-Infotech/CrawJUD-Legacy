"""Gerencia e salva dados de processos PJe em planilhas Excel de forma eficiente.

Este módulo fornece funcionalidades para:
- Processar e formatar dados de processos judiciais do PJe;
- Salvar dados em diferentes planilhas Excel, organizando por tipos de informações;
- Lidar com grandes volumes de dados utilizando lotes para evitar limites do Excel.

"""

from __future__ import annotations

import argparse
import re
import sys
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar
from zoneinfo import ZoneInfo

from clear import clear
from crawjud.utils.models.logs import CachedExecution
from dotenv import load_dotenv
from pandas import DataFrame, ExcelWriter, concat, read_excel
from termcolor import colored
from tqdm import tqdm

if TYPE_CHECKING:
    from collections.abc import Generator

    from crawjud.interfaces.pje import ProcessoJudicialDict as Processo

clear()
load_dotenv()


class SavePjeXlsx:
    """Salve e processe dados de processos PJe em planilhas Excel de forma eficiente.

    Args:
        path_planilha (str): Caminho para o arquivo Excel de saída.

    Returns:
        None: Não retorna valor.

    Raises:
        FileNotFoundError: Caso o caminho do arquivo não exista.

    """

    pid: str
    path_planilha: Path
    pk: str
    data_save: ClassVar[list[dict[str, str]]] = []
    advogados: ClassVar[list[dict[str, str]]] = []
    outras_partes_list: ClassVar[list[dict[str, str]]] = []
    lista_partes_ativo: ClassVar[list[dict[str, str]]] = []
    lista_partes_passivo: ClassVar[list[dict[str, str]]] = []
    list_assuntos: ClassVar[list[dict[str, str]]] = []
    list_anexos: ClassVar[list[dict[str, str]]] = []
    list_movimentacoes: ClassVar[list[dict[str, str]]] = []
    list_dict_representantes: ClassVar[list[dict[str, str]]] = []
    list_expedientes: ClassVar[list[dict[str, str]]] = []
    contagem: ClassVar[int] = 0
    divide_5: ClassVar[int] = 0

    data_query: list[CachedExecution]

    def __init__(self, path_planilha: str, pid: str) -> None:
        """Inicialize a classe com o caminho da planilha e carregue os dados base.

        Args:
            path_planilha (str): Caminho para o arquivo Excel de saída.
            pid(str): pid

        """
        self.pid = pid
        # Inicializa o caminho da planilha e carrega os dados do cache
        self.path_planilha = Path(path_planilha)
        self.data_query = CachedExecution.all_data()
        if self.path_planilha.exists():
            self.path_planilha.unlink()

        with suppress(Exception):
            if not path_planilha.exists():
                with ExcelWriter(
                    str(path_planilha),
                    "openpyxl",
                    mode="w",
                ) as writer:
                    DataFrame().to_excel(
                        excel_writer=writer,
                        sheet_name="Processos",
                    )

    def _append_expedientes(self, data_item: Processo) -> Processo:
        self.list_expedientes.extend([
            {"NUMERO_PROCESSO": self.pk, **item}
            for item in list(
                self.formata_geral(list(data_item.pop("expedientes"))),
            )
        ])

        return data_item

    def _append_itens_processo(self, data_item: Processo) -> None:
        itens_processo: list[dict[str, str]] = data_item.pop(
            "itensProcesso",
        )
        self.list_anexos.extend([
            {"NUMERO_PROCESSO": self.pk, **item}
            for item in list(
                self.formata_anexos(
                    list(
                        filter(
                            lambda x: x.get("anexos"),
                            itens_processo,
                        ),
                    ),
                ),
            )
        ])
        self.list_movimentacoes.extend([
            {"NUMERO_PROCESSO": self.pk, **item}
            for item in self.formata_movimentacao(list(itens_processo))
        ])

        return data_item

    def _append_assuntos(self, data_item: Processo) -> None:
        self.list_assuntos.extend([
            {"NUMERO_PROCESSO": self.pk, **item}
            for item in list(self.formata_assuntos(data_item.pop("assuntos")))
        ])

        return data_item

    def _append_partes(self, data_item: Processo) -> None:
        self.lista_partes_passivo.extend([
            {"NUMERO_PROCESSO": self.pk, **item}
            for item in list(self.formata_partes(data_item.pop("poloPassivo")))
        ])
        self.lista_partes_ativo.extend([
            {"NUMERO_PROCESSO": self.pk, **item}
            for item in list(self.formata_partes(data_item.pop("poloAtivo")))
        ])

        if self.data_item.get("poloOutros"):
            self.outras_partes_list.extend([
                {"NUMERO_PROCESSO": self.pk, **item}
                for item in list(
                    self.formata_partes_terceiros(data_item.pop("poloOutros")),
                )
            ])

        self.advogados.extend([
            {"NUMERO_PROCESSO": self.pk, **item}
            for item in self.list_dict_representantes
        ])

        return data_item

    def _append_geral(self, data_item: Processo) -> Processo:
        self.data_save.extend([
            {"NUMERO_PROCESSO": self.pk, **item}
            for item in list(self.formata_geral([data_item]))
        ])

        return data_item

    def save(self) -> None:
        """Carrega e processa os dados, salvando-os em lotes em diferentes planilhas."""
        kw = {
            "path": self.path_planilha,
            "engine": "openpyxl",
            "mode": "a",
            "if_sheet_exists": "overlay",
        }

        filtered_dataquery = list(
            filter(lambda x: x.pid == self.pid, self.data_query),
        )

        pbar = tqdm(enumerate(filtered_dataquery))

        for item in pbar:
            if not pbar.total:
                pbar.total = int(item.totalpk_s) + 1
                pbar.display()
                self.divide_5 = int(pbar.total / 5)

            self.pk = item.processo
            data_item = item.model_dump()["data"]

            if not data_item.get("numero"):
                tqdm.write(data_item)
                continue

            data_item.pop("numero")

            if data_item.get("expedientes"):
                data_item = self._append_expedientes(data_item=data_item)

            if data_item.get("itensProcesso"):
                data_item = self._append_itens_processo(data_item=data_item)

            data_item = self._append_geral(data_item=data_item)

            if (
                self.contagem == int(self.divide_5)
                or int(pbar.n) + 1 == pbar.total
            ):
                with ExcelWriter(**kw) as writer:
                    saves = [
                        (self.data_save, "Processos", writer),
                        (self.list_assuntos, "Assuntos", writer),
                        (self.outras_partes_list, "Outras Partes", writer),
                        (self.lista_partes_ativo, "Autores", writer),
                        (self.lista_partes_passivo, "Réus", writer),
                        (self.advogados, "Advogados", writer),
                        (self.list_movimentacoes, "Movimentações", writer),
                        (self.list_anexos, "Anexos Movimentações", writer),
                        (self.list_expedientes, "Expedientes", writer),
                    ]
                    for save in saves:
                        self.save_in_batches(*save)
                        save[0].clear()

                    data_save: list[dict[str, str]] = []
                    self.advogados = []
                    self.outras_partes_list = []
                    self.lista_partes_ativo = []
                    self.lista_partes_passivo = []
                    self.list_assuntos: list[dict[str, str]] = []
                    self.list_anexos: list[dict[str, str]] = []
                    self.list_movimentacoes: list[dict[str, str]] = []
                    self.list_expedientes: list[dict[str, str]] = []

                self.contagem = 0

            self.contagem += 1
            self.list_dict_representantes = []

        if len(data_save) > 0:
            with ExcelWriter(**kw) as writer:
                saves = [
                    (self.data_save, "Processos", writer),
                    (self.list_assuntos, "Assuntos", writer),
                    (self.outras_partes_list, "Outras Partes", writer),
                    (self.lista_partes_ativo, "Autores", writer),
                    (self.lista_partes_passivo, "Réus", writer),
                    (self.advogados, "Advogados", writer),
                    (self.list_movimentacoes, "Movimentações", writer),
                    (self.list_anexos, "Anexos Movimentações", writer),
                    (self.list_expedientes, "Expedientes", writer),
                ]
                for save in saves:
                    self.save_in_batches(*save)
                    save[0].clear()

                data_save: list[dict[str, str]] = []
                self.advogados = []
                self.outras_partes_list = []
                self.lista_partes_ativo = []
                self.lista_partes_passivo = []
                self.list_assuntos: list[dict[str, str]] = []
                self.list_anexos: list[dict[str, str]] = []
                self.list_movimentacoes: list[dict[str, str]] = []
                self.list_expedientes: list[dict[str, str]] = []

        tqdm.write(
            colored(
                str(int(pbar.n) + 1 == pbar.total),
                color={"False": "red", "True": "green"}[
                    str(int(pbar.n) + 1 == pbar.total)
                ],
            ),
        )
        tqdm.write("ok")

    def formata_assuntos(
        self,
        lista: list[dict[str, str]],
    ) -> Generator[dict[str, datetime | str], Any, None]:
        for item in lista:
            formated_data = {
                f"{k}".upper(): self.formata_tempo(v)
                for k, v in list(dict(item).items())
                if not isinstance(v, list) or k.lower() != "id"
            }

            yield formated_data

    def formata_endereco(self, endr_dict: dict[str, str]) -> str:
        return " | ".join([
            f"{endr_k.upper()}: {endr_v.strip()}"
            for endr_k, endr_v in list(endr_dict.items())
        ])

    def formata_representantes(
        self,
        lista: list[dict[str, str]],
    ) -> Generator[dict[str, datetime | str], Any, None]:
        for item in lista:
            tipo_parte = item.pop("tipo")
            if item.get("endereco"):
                item.update({
                    "endereco".upper(): self.formata_endereco(
                        item.get("endereco"),
                    ),
                })

            formated_data = {
                f"{k}_{tipo_parte}".upper(): self.formata_tempo(v)
                for k, v in list(dict(item).items())
                if not isinstance(v, list)
                and k.lower() != "utilizaLoginSenha".lower()
                and k.lower() != "situacao".lower()
                and k.lower() != "login".lower()
                and k.lower() != "idPessoa".lower()
            }

            yield formated_data

    def formata_partes(
        self,
        lista: list[dict[str, str]],
    ) -> Generator[dict[str, datetime | str], Any, None]:
        for item in lista:
            polo_parte = item.pop("polo")
            representantes: list[dict[str, str]] = []

            if item.get("endereco"):
                item.update({
                    "endereco".upper(): self.formata_endereco(
                        item.get("endereco"),
                    ),
                })

            if item.get("representantes"):
                representantes = item.pop("representantes")

            if item.get("papeis"):
                item.pop("papeis")

            formated_data = {
                f"{k}_polo_{polo_parte}".upper(): self.formata_tempo(v)
                for k, v in list(dict(item).items())
                if not isinstance(v, list)
                and k.lower() != "utilizaLoginSenha".lower()
                and k.lower() != "situacao".lower()
                and k.lower() != "login".lower()
                and k.lower() != "idPessoa".lower()
            }

            for adv in list(self.formata_representantes(representantes)):
                new_data_ = {"REPRESENTADO": item.get("nome")}
                new_data_.update(adv)
                self.list_dict_representantes.append(new_data_)

            yield formated_data

    def formata_partes_terceiros(
        self,
        lista: list[dict[str, str]],
    ) -> Generator[dict[str, str], Any, None]:
        for item in lista:
            polo_parte = item.pop("polo")
            representantes: list[dict[str, str]] = []

            if item.get("endereco"):
                item.update({
                    "endereco".upper(): self.formata_endereco(
                        item.get("endereco"),
                    ),
                })

            if item.get("representantes"):
                representantes = item.pop("representantes")

            if item.get("papeis"):
                item.pop("papeis")

            formated_data = {
                f"{k}_{polo_parte}".upper(): self.formata_tempo(v)
                for k, v in list(dict(item).items())
                if not isinstance(v, list)
                and k.lower() != "utilizaLoginSenha".lower()
                and k.lower() != "situacao".lower()
                and k.lower() != "login".lower()
                and k.lower() != "idPessoa".lower()
            }

            for adv in list(self.formata_representantes(representantes)):
                new_data_ = {"REPRESENTADO": item.get("nome")}
                new_data_.update(adv)
                self.list_dict_representantes.append(new_data_)

            yield formated_data

    def formata_tempo(
        self,
        *,
        item: str | bool,
    ) -> datetime | float | int | bool | str:
        if isinstance(item, str):
            if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", item):
                return datetime.strptime(
                    item.split(".")[0],
                    "%Y-%m-%dT%H:%M:%S",
                ).replace(tzinfo=ZoneInfo("America/Manaus"))

            if re.match(
                r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}$",
                item,
            ):
                return datetime.strptime(item, "%Y-%m-%dT%H:%M:%S.%f").replace(
                    tzinfo=ZoneInfo("America/Manaus"),
                )

        return item

    def formata_anexos(
        self,
        lista: list[dict[str, str]],
    ) -> Generator[dict[str, str], Any, None]:
        new_lista: list[dict[str, str]] = []
        for item in lista:
            new_lista.extend(item.pop("anexos"))

        for item in new_lista:
            formated_data = {
                k.upper(): self.formata_tempo(v)
                for k, v in list(dict(item).items())
                if not isinstance(v, list)
                and (
                    k.lower() == "id"
                    or k.lower() == "titulo"
                    or k.lower() == "idUnicoDocumento".lower()
                    or k.lower() == "data"
                )
            }

            yield formated_data

    def formata_movimentacao(
        self,
        lista: list[dict[str, str]],
    ) -> Generator[dict[str, str], Any, None]:
        for item in lista:
            if item.get("anexos"):
                item.pop("anexos")

            formated_data = {
                k.upper(): self.formata_tempo(v)
                for k, v in list(dict(item).items())
                if not isinstance(v, list)
                and (
                    k.lower() == "id"
                    or k.lower() == "titulo"
                    or k.lower() == "idUnicoDocumento".lower()
                    or k.lower() == "data"
                    or k.lower() == "usuarioCriador".lower()
                    or k.lower() == "tipoConteudo".lower()
                )
            }

            yield formated_data

    # Salva os dados em lotes para evitar exceder o limite de linhas do Excel
    def save_in_batches(
        self,
        data: list[dict],
        sheet_name: str,
        writer: ExcelWriter,
    ) -> None:
        """Salva os dados em lotes no arquivo Excel para evitar exceder o limite de linhas.

        Args:
            data (list[dict]): Lista de dicionários com os dados a serem salvos.
            sheet_name (str): Nome da planilha no Excel.
            writer (pd.ExcelWriter): Objeto ExcelWriter para escrita.
            batch_size (int): Tamanho do lote de linhas por escrita.

        """
        df = DataFrame(data)
        try:
            existing_df = read_excel(
                str(self.path_planilha),
                sheet_name=sheet_name,
            )
            df_final = concat([existing_df, df])
            df_final.to_excel(writer, sheet_name=sheet_name, index=False)
        except Exception:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    def formata_geral(
        self,
        lista: list[dict[str, str]],
    ) -> Generator[dict[str, datetime | str], Any, None]:
        for item in lista:
            formated_data = {
                k.upper(): self.formata_tempo(v)
                for k, v in list(dict(item).items())
                if not isinstance(v, list)
            }

            yield formated_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Save XLSX PJe.")

    parser.add_argument("--output", required=True, type=str)

    ns = parser.parse_args(sys.argv[1:])

    sav = SavePjeXlsx(path_planilha=ns.output)
    sav.save()
