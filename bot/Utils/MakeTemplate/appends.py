class listas:

    @property
    def emissor_sucesso(self) -> list[str]:
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

        return [
            "Data movimentação",
            "Nome Movimentação",
            "Texto da movimentação",
            "Nome peticionante",
            "Classiicação Peticionante",
        ]

    @property
    def sols_pag_sucesso(self) -> list[str]:

        return [
            "MENSAGEM_COMCLUSAO",
            "TIPO_PGTO",
            "COMPROVANTE_1",
            "ID_PGTO",
            "COMPROVANTE_2",
        ]

    @property
    def sucesso(self) -> list[str]:

        return ["MENSAGEM_COMCLUSAO", "NOME_COMPROVANTE"]

    @property
    def protocolo_sucesso(self) -> list[str]:

        return ["MENSAGEM_COMCLUSAO", "NOME_COMPROVANTE", "ID_PROTOCOLO"]

    @property
    def erro(self) -> list[str]:

        return ["MOTIVO_ERRO"]
