class listas:

    def __init__(self) -> None:
        pass

    def __call__(self, name_list: str) -> list[str]:

        self.lista = getattr(self, name_list, None)
        list = None
        if self.lista:
            list = self.lista()

        return list

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

    def movimentacao_sucesso(self) -> list[str]:

        return [
            "Data movimentação",
            "Nome Movimentação",
            "Texto da movimentação",
            "Nome peticionante",
            "Classiicação Peticionante",
        ]

    def sols_pag_sucesso(self) -> list[str]:

        return [
            "MENSAGEM_COMCLUSAO",
            "TIPO_PGTO",
            "COMPROVANTE_1",
            "ID_PGTO",
            "COMPROVANTE_2",
        ]

    def sucesso(self) -> list[str]:

        return ["MENSAGEM_COMCLUSAO", "NOME_COMPROVANTE"]

    def protocolo_sucesso(self) -> list[str]:

        return ["MENSAGEM_COMCLUSAO", "NOME_COMPROVANTE", "ID_PROTOCOLO"]

    def erro(self) -> list[str]:

        return ["MOTIVO_ERRO"]
