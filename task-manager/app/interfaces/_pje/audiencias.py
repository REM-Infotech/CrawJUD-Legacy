"""Classes para o Json Audiências PJe.

Esta estrutura tipada representa os dados de audiências conforme extraídos do PJe.
"""

from __future__ import annotations

from typing import TypedDict


class JurisdicaoDict(TypedDict):
    """Defina os campos obrigatórios para uma jurisdição conforme estrutura do PJe.

    Args:
        id (int): Identificador único da jurisdição.
        descricao (str): Descrição textual da jurisdição.
        ativo (bool): Indica se a jurisdição está ativa.
        inibeLixeiraGigs (bool): Inibe o uso da lixeira para GIGs.
        codigoOrigem (int): Código de origem da jurisdição.

    Returns:
        TypedDict: Estrutura tipada representando uma jurisdição do PJe.

    """

    id: int
    descricao: str
    ativo: bool
    inibeLixeiraGigs: bool
    codigoOrigem: int


class UsuarioCadastroProcessoDict(TypedDict):
    """Defina os campos obrigatórios para o cadastro de usuário do processo no PJe.

    Args:
        id (int): Identificador único do usuário.
        nome (str): Nome completo do usuário.
        login (str): Login utilizado pelo usuário no sistema.

    Returns:
        TypedDict: Estrutura tipada representando um usuário cadastrado no processo.

    """

    id: int
    nome: str
    login: str


class OrgaoJulgadorCargoDict(TypedDict):
    """Defina os campos obrigatórios para cargos do órgão julgador no PJe.

    Args:
        id (int): Identificador único do cargo.
        descricao (str): Descrição do cargo.
        siglaCargo (str): Sigla do cargo.
        ativo (bool): Indica se o cargo está ativo.
        recebeDistribuicao (bool): Indica se recebe distribuição.
        auxiliar (bool): Indica se é cargo auxiliar.
        valorPeso (float): Valor do peso do cargo.
        pesoDistribuicao (float): Peso para distribuição.
        acumulaMediaDosCargosEspecializados (bool): Acumula média de cargos especializados.
        compensacaoPorProdutividadePorClasse (bool): Compensação por produtividade por classe.

    Returns:
        TypedDict: Estrutura tipada representando um cargo do órgão julgador no PJe.

    """

    id: int
    descricao: str
    siglaCargo: str
    ativo: bool
    recebeDistribuicao: bool
    auxiliar: bool
    valorPeso: float
    pesoDistribuicao: float
    acumulaMediaDosCargosEspecializados: bool
    compensacaoPorProdutividadePorClasse: bool


class OrgaoJulgadorDict(TypedDict):
    """Defina os campos obrigatórios para um órgão julgador conforme estrutura do PJe.

    Args:
        id (int): Identificador único do órgão julgador.
        descricao (str): Descrição do órgão julgador.
        cejusc (bool): Indica se é CEJUSC.
        ativo (bool): Indica se o órgão está ativo.
        sigla (str): Sigla do órgão julgador.
        postoAvancado (bool): Indica se é posto avançado.
        siglaEnvioDejt (str): Sigla para envio DEJT.
        dataCriacao (str): Data de criação do órgão julgador.
        dddTelefone (str): DDD do telefone.
        dddFax (str): DDD do fax.
        numeroTelefone (str): Número do telefone.
        novoOrgaoJulgador (bool): Indica se é novo órgão julgador.
        codigoOrigem (str): Código de origem do órgão julgador.
        instancia (str): Instância do órgão julgador.
        numeroVara (int): Número da vara.
        email (str): E-mail do órgão julgador.
        codigoServentiaCnj (int): Código da serventia no CNJ.

    Returns:
        TypedDict: Estrutura tipada representando um órgão julgador do PJe.

    """

    id: int
    descricao: str
    cejusc: bool
    ativo: bool
    sigla: str
    postoAvancado: bool
    siglaEnvioDejt: str
    dataCriacao: str
    dddTelefone: str
    dddFax: str
    numeroTelefone: str
    novoOrgaoJulgador: bool
    codigoOrigem: str
    instancia: str
    numeroVara: int
    email: str
    codigoServentiaCnj: int


class ClasseJudicialDict(TypedDict):
    """Defina os campos obrigatórios para uma classe judicial conforme estrutura do PJe.

    Args:
        id (int): Identificador único da classe judicial.
        codigo (str): Código da classe judicial.
        descricao (str): Descrição da classe judicial.
        sigla (str): Sigla da classe judicial.
        controlaValorCausa (bool): Indica se controla valor da causa.
        podeIncluirAutoridade (bool): Indica se pode incluir autoridade.
        pisoValorCausa (float): Valor mínimo da causa.
        ativo (bool): Indica se a classe judicial está ativa.
        possuiFilhos (bool): Indica se possui subclasses.

    Returns:
        TypedDict: Estrutura tipada representando uma classe judicial do PJe.

    """

    id: int
    codigo: str
    descricao: str
    sigla: str
    controlaValorCausa: bool
    podeIncluirAutoridade: bool
    pisoValorCausa: float
    ativo: bool
    possuiFilhos: bool


class ProcessoDict(TypedDict):
    """Defina os campos obrigatórios para um processo conforme estrutura do PJe.

    Args:
        id (int): Identificador único do processo.
        numero (str): Número do processo.
        classeJudicial (ClasseJudicialDict): Classe judicial do processo.
        autuadoEm (str): Data de autuação do processo.
        numeroIdentificacaoJustica (int): Número de identificação na Justiça.
        distribuidoEm (str): Data de distribuição do processo.
        valorDaCausa (float): Valor da causa.
        segredoDeJustica (bool): Indica se o processo está em segredo de justiça.
        justicaGratuita (bool): Indica se há justiça gratuita.
        tutelaOuLiminar (bool): Indica se há tutela ou liminar.
        juizoDigital (bool): Indica se o juízo é digital.
        orgaoJulgador (OrgaoJulgadorDict): Órgão julgador do processo.
        orgaoJulgadorCargo (OrgaoJulgadorCargoDict): Cargo do órgão julgador.
        jurisdicao (JurisdicaoDict): Jurisdição do processo.
        mandadoDevolvido (bool): Indica se o mandado foi devolvido.
        dataInicio (str): Data de início do processo.
        usuarioCadastroProcesso (UsuarioCadastroProcessoDict): Usuário que cadastrou o processo.
        selecionadoPauta (bool): Indica se foi selecionado para pauta.
        revisado (bool): Indica se foi revisado.
        outraInstancia (bool): Indica se pertence a outra instância.
        selecionadoJulgamento (bool): Indica se foi selecionado para julgamento.
        apreciadoJusticaGratuita (bool): Indica se a justiça gratuita foi apreciada.
        incidente (bool): Indica se há incidente.
        deveMarcarAudiencia (bool): Indica se deve marcar audiência.
        inRevisao (bool): Indica se está em revisão.
        faseProcessual (str): Fase processual do processo.

    Returns:
        TypedDict: Estrutura tipada representando um processo do PJe.

    """

    id: int
    numero: str
    classeJudicial: ClasseJudicialDict
    autuadoEm: str
    numeroIdentificacaoJustica: int
    distribuidoEm: str
    valorDaCausa: float
    segredoDeJustica: bool
    justicaGratuita: bool
    tutelaOuLiminar: bool
    juizoDigital: bool
    orgaoJulgador: OrgaoJulgadorDict
    orgaoJulgadorCargo: OrgaoJulgadorCargoDict
    jurisdicao: JurisdicaoDict
    mandadoDevolvido: bool
    dataInicio: str
    usuarioCadastroProcesso: UsuarioCadastroProcessoDict
    selecionadoPauta: bool
    revisado: bool
    outraInstancia: bool
    selecionadoJulgamento: bool
    apreciadoJusticaGratuita: bool
    incidente: bool
    deveMarcarAudiencia: bool
    inRevisao: bool
    faseProcessual: str


class SalaFisicaDict(TypedDict):
    """Defina os campos obrigatórios para uma sala física conforme estrutura do PJe.

    Args:
        id (int): Identificador único da sala física.
        nome (str): Nome da sala física.
        orgaoJulgador (OrgaoJulgadorDict): Órgão julgador associado à sala.
        ativo (bool): Indica se a sala física está ativa.

    Returns:
        TypedDict: Estrutura tipada representando uma sala física do PJe.

    """

    id: int
    nome: str
    orgaoJulgador: OrgaoJulgadorDict
    ativo: bool


class TipoAudienciaDict(TypedDict):
    """Defina os campos obrigatórios para um tipo de audiência conforme estrutura do PJe.

    Args:
        id (int): Identificador único do tipo de audiência.
        descricao (str): Descrição do tipo de audiência.
        codigo (str): Código do tipo de audiência.
        isVirtual (bool): Indica se a audiência é virtual.

    Returns:
        TypedDict: Estrutura tipada representando um tipo de audiência do PJe.

    """

    id: int
    descricao: str
    codigo: str
    isVirtual: bool


class AudienciaDict(TypedDict):
    """Defina os campos obrigatórios para uma audiência conforme estrutura do PJe.

    Args:
        id (int): Identificador único da audiência.
        dataInicio (str): Data e hora de início da audiência.
        dataFim (str): Data e hora de término da audiência.
        dataMarcacao (str): Data em que a audiência foi marcada.
        salaFisica (SalaFisicaDict): Sala física onde ocorrerá a audiência.
        status (str): Status atual da audiência.
        idDocumento (int): Identificador do documento associado à audiência.
        processo (ProcessoDict): Processo relacionado à audiência.
        tipo (TipoAudienciaDict): Tipo da audiência.
        designada (bool): Indica se a audiência está designada.
        emAndamento (bool): Indica se a audiência está em andamento.
        documentoAtivo (bool): Indica se o documento da audiência está ativo.

    Returns:
        TypedDict: Estrutura tipada representando uma audiência do PJe.

    """

    id: int
    dataInicio: str
    dataFim: str
    dataMarcacao: str
    salaFisica: SalaFisicaDict
    status: str
    idDocumento: int
    processo: ProcessoDict
    tipo: TipoAudienciaDict
    designada: bool
    emAndamento: bool
    documentoAtivo: bool
