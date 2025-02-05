"""Module: appends.

This module contains utility classes for template configurations.
"""


class listas:  # noqa: N801
    """Utility class providing predefined lists for template processing.

    Attributes:
        emissor_sucesso (list[str]): Fields indicating successful emissor operations.
        esaj_guias_emissao_sucesso (list[str]): Fields indicating successful ESAJ guia emissions.
        capa_sucesso (list[str]): Fields for successful capa operations.
        movimentacao_sucesso (list[str]): Fields indicating successful movimentacao operations.
        sols_pag_sucesso (list[str]): Fields indicating successful sols_pag operations.
        sucesso (list[str]): General success fields.
        protocolo_sucesso (list[str]): Fields indicating successful protocolo operations.
        erro (list[str]): Fields indicating error messages.

    """

    @property
    def emissor_sucesso(self) -> list[str]:
        """Return a list of fields indicating successful emissor operations.

        Return:
            list[str]: List of field names related to emissor success.

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
        """Return a list of fields indicating successful ESAJ guia emissions.

        Return:
            list[str]: List of field names related to ESAJ guia emission success.

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
        """Return a list of fields for successful capa operations.

        Return:
            list[str]: List of field names related to capa success.

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
        """Return a list of fields indicating successful movimentacao operations.

        Return:
            list[str]: List of field names related to movimentacao success.

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
        """Return a list of fields indicating successful sols_pag operations.

        Return:
            list[str]: List of field names related to sols_pag success.

        """
        return ["MENSAGEM_COMCLUSAO", "TIPO_PGTO", "COMPROVANTE_1", "ID_PGTO", "COMPROVANTE_2"]

    @property
    def sucesso(self) -> list[str]:
        """Return a general list of success fields.

        Return:
            list[str]: List of general success field names.

        """
        return ["MENSAGEM_COMCLUSAO", "NOME_COMPROVANTE"]

    @property
    def protocolo_sucesso(self) -> list[str]:
        """Return a list of fields indicating successful protocolo operations.

        Return:
            list[str]: List of field names related to protocolo success.

        """
        return ["MENSAGEM_COMCLUSAO", "NOME_COMPROVANTE", "ID_PROTOCOLO"]

    @property
    def erro(self) -> list[str]:
        """Return a list of fields indicating error messages.

        Return:
            list[str]: List of error message field names.

        """
        return ["MOTIVO_ERRO"]
