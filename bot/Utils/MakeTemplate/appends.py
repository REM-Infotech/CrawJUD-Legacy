"""Module: appends.

This module contains utility classes for template configurations.
"""


class Listas:  # noqa: N801
    """Provide predefined lists for template processing.

    Attributes:
        emissor_sucesso (list[str]): Fields for successful emissor operations.
        esaj_guias_emissao_sucesso (list[str]): Fields for successful ESAJ guia emissions.
        capa_sucesso (list[str]): Fields for successful capa operations.
        movimentacao_sucesso (list[str]): Fields for successful movimentacao operations.
        sols_pag_sucesso (list[str]): Fields for successful sols_pag operations.
        sucesso (list[str]): General success fields.
        protocolo_sucesso (list[str]): Fields for successful protocolo operations.
        erro (list[str]): Fields for error messages.

    """

    @property
    def emissor_sucesso(self) -> list[str]:
        """Return list of field names for successful emissor operations.

        Returns:
            list[str]: Field names related to emissor success.

        """
        return [
            "Descrição do Prazo",
            "Valor do documento",
            "Data para pagamento",
            "Tipo de pagamento",
            "Solicitante",
            "Condenação",
            "Código de Barras",
            "Nome Documento",
        ]

    @property
    def esaj_guias_emissao_sucesso(self) -> list[str]:
        """Return list of field names for successful ESAJ guia emissions.

        Returns:
            list[str]: Field names related to ESAJ guia emission success.

        """
        return [
            "Tipo Guia",
            "Valor do documento",
            "Data para pagamento",
            "Tipo de pagamento",
            "Solicitante",
            "Condenação",
            "Código de Barras",
            "Nome Documento",
        ]

    @property
    def capa_sucesso(self) -> list[str]:
        """Return list of field names for successful capa operations.

        Returns:
            list[str]: Field names related to capa success.

        """
        return [
            "AREA_DIREITO",
            "SUBAREA_DIREITO",
            "ESTADO",
            "COMARCA",
            "FORO",
            "VARA",
            "DATA_DISTRIBUICAO",
            "PARTE_CONTRARIA",
            "TIPO_PARTE_CONTRARIA",
            "DOC_PARTE_CONTRARIA",
            "EMPRESA",
            "TIPO_EMPRESA",
            "DOC_EMPRESA",
            "ACAO",
            "ADVOGADO_INTERNO",
            "ADV_PARTE_CONTRARIA",
            "ESCRITORIO_EXTERNO",
            "VALOR_CAUSA",
        ]

    @property
    def movimentacao_sucesso(self) -> list[str]:
        """Return list of field names for successful movimentacao operations.

        Returns:
            list[str]: Field names related to movimentacao success.

        """
        return [
            "Data movimentação",
            "Nome Movimentação",
            "Texto da movimentação",
            "Nome peticionante",
            "Classiicação Peticionante",
        ]

    @property
    def sols_pag_sucesso(self) -> list[str]:
        """Return list of field names for successful sols_pag operations.

        Returns:
            list[str]: Field names related to sols_pag success.

        """
        return ["MENSAGEM_COMCLUSAO", "TIPO_PGTO", "COMPROVANTE_1", "ID_PGTO", "COMPROVANTE_2"]

    @property
    def sucesso(self) -> list[str]:
        """Return list of general success field names.

        Returns:
            list[str]: General success field names.

        """
        return ["MENSAGEM_COMCLUSAO", "NOME_COMPROVANTE"]

    @property
    def protocolo_sucesso(self) -> list[str]:
        """Return list of field names for successful protocolo operations.

        Returns:
            list[str]: Field names related to protocolo success.

        """
        return ["MENSAGEM_COMCLUSAO", "NOME_COMPROVANTE", "ID_PROTOCOLO"]

    @property
    def erro(self) -> list[str]:
        """Return list of field names for error messages.

        Returns:
            list[str]: Error message field names.

        """
        return ["MOTIVO_ERRO"]
